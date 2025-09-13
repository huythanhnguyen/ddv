import { ProductDisplayMessage } from '@/types/product';

export interface ParsedMessage {
  type: 'text' | 'product-display';
  text: string;
  productData?: ProductDisplayMessage;
}

// Helper function to clean JSON string before parsing
function cleanJsonString(jsonString: string): string {
  // Replace Python None with JSON null
  let cleaned = jsonString.replace(/: None/g, ': null');
  cleaned = cleaned.replace(/: None,/g, ': null,');
  cleaned = cleaned.replace(/: None}/g, ': null}');
  cleaned = cleaned.replace(/: None]/g, ': null]');
  
  // Replace Python True/False with JSON true/false
  cleaned = cleaned.replace(/: True/g, ': true');
  cleaned = cleaned.replace(/: False/g, ': false');
  
  // Remove trailing commas before closing brackets/braces
  cleaned = cleaned.replace(/,(\s*[}\]])/g, '$1');
  
  return cleaned;
}

export function parseMessage(content: string): ParsedMessage {
  // Debug logging only in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[MessageParser] Parsing message:', content.substring(0, 200) + '...');
  }
  
  // Handle error messages first
  if (content.includes('Lỗi khi') || content.includes('Error:') || content.includes('Exception:')) {
    return {
      type: 'text',
      text: content
    };
  }
  
  // Try multiple JSON detection patterns
  let jsonText = '';
  
  // Pattern 1: JSON in markdown code blocks (```json...```)
  const markdownJsonMatch = content.match(/```json\s*(\{[\s\S]*?\})\s*```/);
  if (markdownJsonMatch) {
    jsonText = markdownJsonMatch[1];
    if (process.env.NODE_ENV === 'development') {
      console.log('[MessageParser] Found markdown JSON:', jsonText.substring(0, 100) + '...');
    }
  } else {
    // Pattern 2: JSON in plain code blocks (```...```)
    const plainCodeMatch = content.match(/```\s*(\{[\s\S]*?\})\s*```/);
    if (plainCodeMatch) {
      jsonText = plainCodeMatch[1];
      if (process.env.NODE_ENV === 'development') {
        console.log('[MessageParser] Found plain code JSON:', jsonText.substring(0, 100) + '...');
      }
    } else {
      // Pattern 3: Standalone JSON object (no code blocks) - improved pattern
      const standaloneJsonMatch = content.match(/(\{[\s\S]*?"type"\s*:\s*"product-display"[\s\S]*?"products"\s*:\s*\[[\s\S]*?\][\s\S]*?\})/);
      if (standaloneJsonMatch) {
        jsonText = standaloneJsonMatch[1];
        if (process.env.NODE_ENV === 'development') {
          console.log('[MessageParser] Found standalone JSON:', jsonText.substring(0, 100) + '...');
        }
      } else {
        // Pattern 4: Multi-line JSON without code blocks (more flexible)
        const lines = content.split('\n');
        let jsonStart = -1;
        let jsonEnd = -1;
        let braceCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          if (line.startsWith('{') && (line.includes('"type"') || line.includes('"product-display"') || i < lines.length - 1 && lines[i + 1].includes('"type"'))) {
            jsonStart = i;
            braceCount = 1;
          } else if (jsonStart >= 0) {
            for (let char of line) {
              if (char === '{') braceCount++;
              if (char === '}') braceCount--;
            }
            if (braceCount === 0) {
              jsonEnd = i;
              break;
            }
          }
        }
        
        if (jsonStart >= 0 && jsonEnd >= 0) {
          jsonText = lines.slice(jsonStart, jsonEnd + 1).join('\n');
          if (process.env.NODE_ENV === 'development') {
            console.log('[MessageParser] Found multi-line JSON:', jsonText.substring(0, 100) + '...');
          }
        } else {
          // Pattern 5: Try to find any JSON object that might contain products
          const anyJsonMatch = content.match(/(\{[\s\S]*?"products"\s*:\s*\[[\s\S]*?\][\s\S]*?\})/);
          if (anyJsonMatch) {
            jsonText = anyJsonMatch[1];
            if (process.env.NODE_ENV === 'development') {
              console.log('[MessageParser] Found JSON with products array:', jsonText.substring(0, 100) + '...');
            }
          } else {
            // Pattern 6: Look for JSON-like structure with product-display type
            const productDisplayMatch = content.match(/\{[^{}]*"type"\s*:\s*"product-display"[^{}]*\}/);
            if (productDisplayMatch) {
              // Try to extract the full JSON object
              const startIndex = content.indexOf(productDisplayMatch[0]);
              let braceCount = 0;
              let endIndex = startIndex;
              
              for (let i = startIndex; i < content.length; i++) {
                if (content[i] === '{') braceCount++;
                if (content[i] === '}') {
                  braceCount--;
                  if (braceCount === 0) {
                    endIndex = i;
                    break;
                  }
                }
              }
              
              if (endIndex > startIndex) {
                jsonText = content.substring(startIndex, endIndex + 1);
                if (process.env.NODE_ENV === 'development') {
                  console.log('[MessageParser] Found product-display JSON structure:', jsonText.substring(0, 100) + '...');
                }
              }
            } else {
              // Pattern 7: Look for JSON starting with { and containing product-display
              let startIdx = content.indexOf('{');
              if (startIdx !== -1) {
                let braceCount = 0;
                let endIdx = startIdx;
                
                for (let i = startIdx; i < content.length; i++) {
                  if (content[i] === '{') braceCount++;
                  if (content[i] === '}') {
                    braceCount--;
                    if (braceCount === 0) {
                      endIdx = i;
                      break;
                    }
                  }
                }
                
                if (endIdx > startIdx) {
                  const potentialJson = content.substring(startIdx, endIdx + 1);
                  if (potentialJson.includes('"type"') && potentialJson.includes('"product-display"')) {
                    jsonText = potentialJson;
                    if (process.env.NODE_ENV === 'development') {
                      console.log('[MessageParser] Found JSON by brace matching:', jsonText.substring(0, 100) + '...');
                    }
                  }
                }
              }
              
              if (!jsonText) {
                if (process.env.NODE_ENV === 'development') {
                  console.log('[MessageParser] No JSON pattern found in message');
                }
              }
            }
          }
        }
      }
    }
  }
  
  // Try to parse the detected JSON
  if (jsonText) {
    try {
      // Clean the JSON string first
      let cleanJsonText = cleanJsonString(jsonText);
      
      // Handle escaped JSON strings (common in last_coordinator_response)
      if (cleanJsonText.includes('\\n')) {
        cleanJsonText = cleanJsonText.replace(/\\n/g, '\n');
      }
      if (cleanJsonText.includes('\\"')) {
        cleanJsonText = cleanJsonText.replace(/\\"/g, '"');
      }
      if (cleanJsonText.includes('\\\\')) {
        cleanJsonText = cleanJsonText.replace(/\\\\/g, '\\');
      }
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[MessageParser] Cleaned JSON text:', cleanJsonText.substring(0, 200) + '...');
      }
      
      const parsedData = JSON.parse(cleanJsonText);
      if (process.env.NODE_ENV === 'development') {
        console.log('[MessageParser] Successfully parsed JSON:', parsedData);
      }
      
      // Check if it's a product display message
      if (parsedData.type === 'product-display' && parsedData.products && Array.isArray(parsedData.products)) {
        if (process.env.NODE_ENV === 'development') {
          console.log('[MessageParser] Detected product-display with', parsedData.products.length, 'products');
        }
        
        // Validate and clean product data
        const validProducts = parsedData.products.filter(product => {
          if (!product || typeof product !== 'object') return false;
          
          // Check required fields
          const hasRequiredFields = product.id && product.name && product.price && product.image;
          if (!hasRequiredFields) {
            if (process.env.NODE_ENV === 'development') {
              console.warn('[MessageParser] Invalid product missing required fields:', product);
            }
            return false;
          }
          
          // Validate price structure
          if (!product.price.current || typeof product.price.current !== 'number') {
            if (process.env.NODE_ENV === 'development') {
              console.warn('[MessageParser] Invalid product price:', product.price);
            }
            return false;
          }
          
          // Validate image structure
          if (!product.image.url || typeof product.image.url !== 'string') {
            if (process.env.NODE_ENV === 'development') {
              console.warn('[MessageParser] Invalid product image:', product.image);
            }
            return false;
          }
          
          return true;
        });
        
        if (process.env.NODE_ENV === 'development') {
          console.log('[MessageParser] Valid products after filtering:', validProducts.length);
        }
        
        // Update parsedData with validated products
        parsedData.products = validProducts;
        
        // Clean the text by removing the JSON part
        let cleanText = content;
        if (markdownJsonMatch) {
          cleanText = content.replace(/```json[\s\S]*?```/g, '').trim();
        } else {
          cleanText = content.replace(jsonText, '').trim();
        }
        
        // If cleanText is empty or contains only whitespace/newlines, use the message from the JSON
        if (!cleanText || cleanText.match(/^\s*$/) || cleanText === jsonText) {
          cleanText = parsedData.message || '';
        }
        
        // Remove duplicate content - if cleanText contains the same content as JSON message
        if (cleanText && parsedData.message && cleanText.includes(parsedData.message)) {
          cleanText = parsedData.message;
        }
        
        // Handle thinking/processing messages that might be duplicated
        // Handle both markdown and non-markdown thinking patterns
        if (cleanText && (cleanText.includes('🔍 **Phân tích:**') || cleanText.includes('🔍 Phân tích:'))) {
          // Extract the first occurrence of the thinking pattern (both markdown and non-markdown)
          const thinkingPatterns = [
            /🔍 \*\*Phân tích:\*\*[^🔄]*🔄 \*\*Đang thực hiện:\*\*[^✅]*✅ \*\*Hoàn thành:\*\*[^🔍]*/,
            /🔍 Phân tích:[^🔄]*🔄 Đang thực hiện:[^✅]*✅ Hoàn thành:[^🔍]*/,
            /🔍 \*\*Phân tích:\*\*[^🔄]*🔄 \*\*Đang thực hiện:\*\*/,
            /🔍 Phân tích:[^🔄]*🔄 Đang thực hiện:[^🔍]*/
          ];
          
          for (const pattern of thinkingPatterns) {
            const match = cleanText.match(pattern);
            if (match) {
              cleanText = match[0];
              break;
            }
          }
        }
        
        // Remove completely duplicate content patterns
        // Split by common thinking separators and take only unique parts (both markdown and non-markdown)
        if (cleanText && (cleanText.includes('🔍 **Phân tích:**') || cleanText.includes('🔍 Phân tích:') || 
                         cleanText.includes('🔄 **Đang thực hiện:**') || cleanText.includes('🔄 Đang thực hiện:') ||
                         cleanText.includes('✅ **Hoàn thành:**') || cleanText.includes('✅ Hoàn thành:'))) {
          const parts = cleanText.split(/(?=🔍 \*\*Phân tích:\*\*|🔍 Phân tích:|🔄 \*\*Đang thực hiện:\*\*|🔄 Đang thực hiện:|✅ \*\*Hoàn thành:\*\*|✅ Hoàn thành:)/);
          const uniqueParts = parts.filter((part, index, arr) => {
            if (!part.trim()) return false;
            // Check if this part is a duplicate of any previous part
            return !arr.slice(0, index).some(prevPart => 
              prevPart.trim() && part.trim() === prevPart.trim()
            );
          });
          cleanText = uniqueParts.join('').trim();
        }
        
        // Additional cleanup for thinking messages that might have repeated patterns
        if (cleanText && (cleanText.includes('🔍 **Phân tích:**') || cleanText.includes('🔍 Phân tích:'))) {
          // Remove any duplicate thinking patterns that might be concatenated (both markdown and non-markdown)
          const thinkingPatterns = [
            /🔍 \*\*Phân tích:\*\*[^🔍]*/g,
            /🔍 Phân tích:[^🔍]*/g
          ];
          
          for (const pattern of thinkingPatterns) {
            const matches = cleanText.match(pattern);
            if (matches && matches.length > 1) {
              // Take only the first complete thinking pattern
              const firstMatch = matches[0];
              const nextPatternIndex = cleanText.indexOf(matches[0].includes('**') ? '🔍 **Phân tích:**' : '🔍 Phân tích:', firstMatch.length);
              if (nextPatternIndex > 0) {
                cleanText = cleanText.substring(0, nextPatternIndex).trim();
              }
              break;
            }
          }
        }
        
        return {
          type: 'product-display',
          text: cleanText,
          productData: parsedData
        };
      } else {
        if (process.env.NODE_ENV === 'development') {
          console.log('[MessageParser] JSON is not product-display type or missing products array:', parsedData.type, parsedData.products);
        }
      }
    } catch (error) {
      console.warn('[MessageParser] Failed to parse JSON:', error);
      console.warn('[MessageParser] JSON text was:', jsonText);
      
      // Try to fix common JSON issues and retry
      try {
        let fixedJson = jsonText;
        
        // Fix common Python JSON issues
        fixedJson = fixedJson.replace(/: None/g, ': null');
        fixedJson = fixedJson.replace(/: True/g, ': true');
        fixedJson = fixedJson.replace(/: False/g, ': false');
        fixedJson = fixedJson.replace(/,(\s*[}\]])/g, '$1'); // Remove trailing commas
        
        const parsedData = JSON.parse(fixedJson);
        if (parsedData.type === 'product-display' && parsedData.products && Array.isArray(parsedData.products)) {
          console.log('[MessageParser] Successfully parsed fixed JSON');
          return {
            type: 'product-display',
            text: content.replace(jsonText, '').trim() || parsedData.message || '',
            productData: parsedData
          };
        }
      } catch (retryError) {
        console.warn('[MessageParser] Failed to parse fixed JSON as well:', retryError);
      }
    }
  }
  
  // Default to text message
  if (process.env.NODE_ENV === 'development') {
    console.log('[MessageParser] Returning as text message');
  }
  
  // Clean thinking content from final text display
  let cleanContent = content;
  
  // Remove thinking patterns from final display - but keep completion message
  const thinkingPatterns = [
    /🔍 \*\*Phân tích:\*\*[^🔄]*🔄 \*\*Đang thực hiện:\*\*[^🔍]*/g,
    /🔍 Phân tích:[^🔄]*🔄 Đang thực hiện:[^🔍]*/g
  ];
  
  for (const pattern of thinkingPatterns) {
    cleanContent = cleanContent.replace(pattern, '');
  }
  
  // Clean up extra whitespace and newlines
  cleanContent = cleanContent.replace(/\n\s*\n/g, '\n').trim();
  
  // Remove duplicate content patterns
  // Check if the content contains the same text repeated
  if (cleanContent) {
    // First, check if the entire content is duplicated
    const halfLength = Math.floor(cleanContent.length / 2);
    const firstHalf = cleanContent.substring(0, halfLength);
    const secondHalf = cleanContent.substring(halfLength);
    
    // If first half and second half are very similar (allowing for minor differences)
    if (firstHalf.trim() === secondHalf.trim()) {
      cleanContent = firstHalf.trim();
    } else {
      // Check for duplicate lines
      const lines = cleanContent.split('\n').filter(line => line.trim());
      if (lines.length >= 2) {
        // Check if first and second lines are identical
        if (lines[0] === lines[1]) {
          // Remove duplicate lines
          const uniqueLines = [lines[0]];
          for (let i = 1; i < lines.length; i++) {
            if (lines[i] !== lines[i-1]) {
              uniqueLines.push(lines[i]);
            }
          }
          cleanContent = uniqueLines.join('\n');
        }
        
        // Check for duplicate paragraphs (same content repeated)
        const paragraphs = cleanContent.split(/\n\s*\n/).filter(p => p.trim());
        if (paragraphs.length >= 2) {
          const uniqueParagraphs = [paragraphs[0]];
          for (let i = 1; i < paragraphs.length; i++) {
            if (paragraphs[i] !== paragraphs[i-1]) {
              uniqueParagraphs.push(paragraphs[i]);
            }
          }
          cleanContent = uniqueParagraphs.join('\n\n');
        }
      }
    }
  }
  
  return {
    type: 'text',
    text: cleanContent || content // Fallback to original if cleaned is empty
  };
}

export function extractProductData(content: string): ProductDisplayMessage | null {
  const parsedMessage = parseMessage(content);
  return parsedMessage.type === 'product-display' ? parsedMessage.productData || null : null;
}

export function cleanMessageText(content: string): string {
  // Remove JSON blocks from message content using the same logic as parseMessage
  let cleanedContent = content;
  
  // Remove markdown JSON blocks
  cleanedContent = cleanedContent.replace(/```json[\s\S]*?```/g, '');
  
  // Remove plain code blocks that might contain JSON
  cleanedContent = cleanedContent.replace(/```\s*\{[\s\S]*?\}\s*```/g, '');
  
  // Remove standalone JSON objects
  cleanedContent = cleanedContent.replace(/\{[^{}]*"type"\s*:\s*"product-display"[^{}]*"products"\s*:[\s\S]*?\}/g, '');
  
  return cleanedContent.trim();
}

export function isErrorMessage(content: string): boolean {
  const errorPatterns = [
    /Lỗi khi/,
    /Rất tiếc, đã xảy ra lỗi/,
    /Error:/,
    /Exception:/,
    /Traceback/,
    /TypeError/,
    /ValueError/,
    /AttributeError/,
    /KeyError/,
    /float\(\) argument must be/,
    /not 'dict'/,
    /not 'str'/,
    /not 'int'/,
    /đã xảy ra lỗi/,
    /không thể/,
    /thất bại/
  ];
  
  return errorPatterns.some(pattern => pattern.test(content));
}

export function extractErrorDetails(content: string): { type: string; message: string; suggestion?: string } | null {
  if (!isErrorMessage(content)) return null;
  
  // Common error patterns and their suggestions
  const errorMappings = [
    {
      pattern: /float\(\) argument must be a string or a real number, not 'dict'/,
      type: 'Data Type Error',
      message: 'Lỗi chuyển đổi kiểu dữ liệu - đang cố gắng chuyển đổi từ điển thành số',
      suggestion: 'Cần kiểm tra và sửa lỗi xử lý dữ liệu sản phẩm'
    },
    {
      pattern: /Rất tiếc, đã xảy ra lỗi khi lấy thông tin chi tiết/,
      type: 'Product Detail Error',
      message: 'Không thể lấy thông tin chi tiết sản phẩm',
      suggestion: 'Vui lòng thử lại hoặc chọn sản phẩm khác'
    },
    {
      pattern: /Lỗi khi so sánh sản phẩm/,
      type: 'Product Comparison Error',
      message: 'Không thể so sánh sản phẩm',
      suggestion: 'Vui lòng thử lại với các sản phẩm khác'
    },
    {
      pattern: /Không tìm thấy sản phẩm/,
      type: 'Product Not Found',
      message: 'Không tìm thấy sản phẩm phù hợp',
      suggestion: 'Vui lòng thử tìm kiếm với từ khóa khác'
    },
    {
      pattern: /đã xảy ra lỗi/,
      type: 'General Error',
      message: 'Đã xảy ra lỗi trong quá trình xử lý',
      suggestion: 'Vui lòng thử lại sau'
    }
  ];
  
  for (const mapping of errorMappings) {
    if (mapping.pattern.test(content)) {
      return mapping;
    }
  }
  
  return {
    type: 'Unknown Error',
    message: 'Đã xảy ra lỗi không xác định',
    suggestion: 'Vui lòng thử lại sau'
  };
}

// Test function for debugging (only in development)
export function testMessageParser() {
  if (process.env.NODE_ENV !== 'development') {
    return;
  }
  
  const testCases = [
    {
      name: 'Simple product display JSON',
      content: '{"type": "product-display", "message": "Test", "products": []}',
      expected: 'product-display'
    },
    {
      name: 'Python None values in JSON',
      content: '{"type": "product-display", "message": "Test", "products": [{"id": "test", "sku": None}]}',
      expected: 'product-display'
    },
    {
      name: 'Duplicate greeting message',
      content: 'Chào bạn! Rất vui được gặp bạn. Tôi có thể giúp bạn tìm hiểu thông tin về Di Động Việt.\nChào bạn! Rất vui được gặp bạn. Tôi có thể giúp bạn tìm hiểu thông tin về Di Động Việt.',
      expected: 'text'
    },
    {
      name: 'Error message detection',
      content: 'Rất tiếc, đã xảy ra lỗi khi lấy thông tin chi tiết về iPhone 16 Pro Max 512GB. Tuy nhiên, tôi có thể cung cấp cho bạn thông tin tóm tắt sau:',
      expected: 'text'
    },
    {
      name: 'Error message with product data',
      content: 'Rất tiếc, đã xảy ra lỗi khi lấy thông tin chi tiết về iPhone 16 Pro Max 512GB. Tuy nhiên, tôi có thể cung cấp cho bạn thông tin tóm tắt sau:\n\n{"type": "product-display", "message": "Test", "products": []}',
      expected: 'product-display'
    }
  ];
  
  testCases.forEach(testCase => {
    const result = parseMessage(testCase.content);
    console.log(`[Test] ${testCase.name}:`, {
      expected: testCase.expected,
      actual: result.type,
      success: result.type === testCase.expected
    });
  });
} 