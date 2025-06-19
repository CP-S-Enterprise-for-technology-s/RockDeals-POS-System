import React from 'react';

const Products = () => {
  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Product Management</h1>
      </div>
      
      <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
        <div className="text-center py-12">
          <h3 className="text-lg font-semibold text-foreground mb-2">Product Management Module</h3>
          <p className="text-muted-foreground">
            Product management features will be implemented here.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Products;

