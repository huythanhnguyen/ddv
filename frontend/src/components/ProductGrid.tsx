import React from 'react';
import ProductCard from '@/components/ProductCard';
import { ProductGridProps } from '@/types/product';
import { cartService } from '@/services/cartService';

const ProductGrid: React.FC<ProductGridProps> = React.memo(({ 
  products, 
  onAddToCart, 
  onViewDetails 
}) => {
  
  // Debug logging only in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[ProductGrid] Received products:', products);
    console.log('[ProductGrid] Products type:', typeof products);
    console.log('[ProductGrid] Products length:', products?.length);
    console.log('[ProductGrid] Products array:', Array.isArray(products));
  }
  
  // Handle error cases
  if (!products) {
    if (process.env.NODE_ENV === 'development') {
      console.log('[ProductGrid] Products is null/undefined');
    }
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-red-500 mb-2">⚠️</div>
        <div>Không có dữ liệu sản phẩm</div>
      </div>
    );
  }
  
  const handleAddToCart = async (product: any) => {
    try {
      const result = await cartService.addToCart({
        sku: product.sku,
        quantity: 1,
        useArtNo: true
      });
      
      if (result.success) {
        console.log('Product added to cart:', product.name);
        // Could show a toast notification here
      } else {
        console.error('Failed to add to cart:', result.error);
        // Could show error notification here
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
    
    // Call parent handler if provided
    onAddToCart?.(product);
  };

  const handleViewDetails = (product: any) => {
    console.log('Viewing product details:', product.name);
    onViewDetails?.(product);
  };

  // Validate products array
  if (!products || !Array.isArray(products) || products.length === 0) {
    if (process.env.NODE_ENV === 'development') {
      console.log('[ProductGrid] No valid products to display:', products);
    }
    return (
      <div className="text-center py-8 text-gray-500">
        Không có sản phẩm nào để hiển thị
      </div>
    );
  }
  
  // Filter out invalid products with detailed validation
  const validProducts = products.filter(product => {
    if (!product || typeof product !== 'object') {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[ProductGrid] Invalid product - not an object:', product);
      }
      return false;
    }
    
    // Check required fields
    if (!product.id || !product.name || !product.price) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[ProductGrid] Invalid product - missing required fields:', {
          id: product.id,
          name: product.name,
          price: product.price
        });
      }
      return false;
    }
    
    // Validate price structure
    if (!product.price.current || typeof product.price.current !== 'number') {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[ProductGrid] Invalid product - invalid price:', product.price);
      }
      return false;
    }
    
    // Validate image structure
    if (!product.image || !product.image.url || typeof product.image.url !== 'string') {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[ProductGrid] Invalid product - invalid image:', product.image);
      }
      return false;
    }
    
    return true;
  });
  
  if (validProducts.length === 0) {
    if (process.env.NODE_ENV === 'development') {
      console.log('[ProductGrid] No valid products after filtering:', products);
    }
    return (
      <div className="text-center py-8 text-gray-500">
        Sản phẩm không hợp lệ
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Grid container with responsive columns: 2 products/row mobile, 3 products/row desktop */}
      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-2 sm:gap-3 md:gap-4 lg:gap-6">
        {validProducts.map((product, index) => (
          <div 
            key={product.id} 
            className="w-full min-w-0 animate-slide-up"
            style={{
              animationDelay: `${index * 50}ms`
            }}
          >
            <ProductCard
              product={product}
              onAddToCart={handleAddToCart}
              onViewDetails={handleViewDetails}
            />
          </div>
        ))}
      </div>
      
      {/* Product count info */}
      <div className="mt-3 sm:mt-4 text-center text-xs sm:text-sm text-gray-500 px-2">
        Hiển thị {validProducts.length} sản phẩm
        {validProducts.length !== products.length && (
          <span className="text-orange-500 ml-2 block sm:inline">
            ({products.length - validProducts.length} sản phẩm không hợp lệ đã bị loại bỏ)
          </span>
        )}
      </div>
    </div>
  );
});

ProductGrid.displayName = 'ProductGrid';

export default ProductGrid; 