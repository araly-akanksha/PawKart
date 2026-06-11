async function fetchProductsAndRender() {
  try {
    const res = await fetch('http://localhost:8000/products');
    if (!res.ok) throw new Error('Failed to fetch products');
    const products = await res.json();
    
    productData = {}; // Clear hardcoded data
    
    products.forEach(p => {
      let category = 'dog';
      const backendCat = (p.category || '').toLowerCase();
      const nameLower = (p.product_name || p.name || '').toLowerCase();
      
      if (backendCat.includes('cat') || nameLower.includes('cat') || nameLower.includes('whiskas')) category = 'cat';
      else if (backendCat.includes('bird') || nameLower.includes('bird') || nameLower.includes('parrot') || nameLower.includes('budgie')) category = 'bird';
      else if (backendCat.includes('fish') || backendCat.includes('aquarium') || nameLower.includes('fish') || nameLower.includes('aquarium')) category = 'aquarium';
      else if (backendCat.includes('toy') || nameLower.includes('toy') || nameLower.includes('bone')) category = 'toys';
      else if (backendCat.includes('health') || backendCat.includes('grooming') || nameLower.includes('shampoo')) category = 'health';
      
      let badge = '';
      if (nameLower.includes('organic')) badge = 'Organic';
      if (nameLower.includes('premium')) badge = 'Best Seller';

      let image = p.image || '../IMG/product_dog_food.png';
      if (!p.image || p.image.includes('placehold.co')) {
        if (category === 'cat') image = '../IMG/product_cat_toys.png';
        if (category === 'health') image = '../IMG/product_shampoo.png';
        if (category === 'bird') image = '../IMG/product_bird_feed.png';
      }

      productData[p.id.toString()] = {
        name: p.product_name || p.name,
        price: p.price,
        image: image,
        category: category,
        rating: 4.5,
        reviewsCount: 100,
        description: p.product_name || p.name || 'No description available',
        badge: badge,
        highlights: ['Premium quality', 'Vet recommended'],
        ratingBreakdown: { 5: 80, 4: 10, 3: 5, 2: 3, 1: 2 },
        reviews: []
      };
    });

    renderFeaturedProducts();
  } catch(e) {
    console.error('Error fetching products', e);
  }
}


fetchProductsAndRender().then(() => console.log('Done')).catch(console.error);