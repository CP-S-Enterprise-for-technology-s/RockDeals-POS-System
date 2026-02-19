import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  ShoppingCart, 
  Users, 
  Package,
  DollarSign,
  Monitor,
  Gamepad2,
  Sofa
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const Dashboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('Today');
  const [selectedYear, setSelectedYear] = useState('This year');
  const [stats, setStats] = useState({
    total_sales: "$0",
    total_orders: "0",
    total_visitors: "0",
    total_sold_products: "0",
    sales_change: "0%",
    orders_change: "0%",
    visitors_change: "0%",
    products_change: "0%"
  });
  const [customerHabitsData, setCustomerHabitsData] = useState([]);
  const [productStatsData, setProductStatsData] = useState([]);
  const [customerGrowthData, setCustomerGrowthData] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Fetch stats
        const statsRes = await fetch(`${API_URL}/dashboard/stats`);
        const statsData = await statsRes.json();
        setStats(statsData);

        // Fetch customer habits
        const habitsRes = await fetch(`${API_URL}/dashboard/customer-habits`);
        const habitsData = await habitsRes.json();
        setCustomerHabitsData(habitsData);

        // Fetch product stats
        const prodRes = await fetch(`${API_URL}/dashboard/product-stats`);
        const prodData = await prodRes.json();
        const colors = ['#8B5CF6', '#EC4899', '#06B6D4', '#F59E0B', '#10B981'];
        setProductStatsData(prodData.categories.map((cat, index) => ({
          ...cat,
          color: colors[index % colors.length]
        })));

        // Fetch customer growth
        const growthRes = await fetch(`${API_URL}/dashboard/customer-growth`);
        const growthData = await growthRes.json();
        setCustomerGrowthData(growthData);

        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const StatCard = ({ title, value, change, icon: Icon, isPositive, isPrimary = false }) => (
    <Card className={`${isPrimary ? 'rockdeals-gradient text-white' : 'bg-card border border-border'}`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isPrimary ? 'bg-white/20' : 'bg-muted'}`}>
              <Icon className={`w-5 h-5 ${isPrimary ? 'text-white' : 'text-foreground'}`} />
            </div>
            <div>
              <p className={`text-sm ${isPrimary ? 'text-white/80' : 'text-muted-foreground'}`}>
                {title}
              </p>
              <p className={`text-2xl font-bold ${isPrimary ? 'text-white' : 'text-foreground'}`}>
                {value}
              </p>
            </div>
          </div>
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
            isPositive 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-red-500/20 text-red-400'
          }`}>
            {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {change}
          </div>
        </div>
        <p className={`text-xs mt-2 ${isPrimary ? 'text-white/60' : 'text-muted-foreground'}`}>
          Product vs last month
        </p>
      </CardContent>
    </Card>
  );

  const ProductStatsCard = () => (
    <Card className="bg-card border border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg font-semibold">Product statistics</CardTitle>
        <Button variant="outline" size="sm" className="text-xs">
          {selectedPeriod} ▼
        </Button>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-3xl font-bold">9,829</p>
            <p className="text-sm text-muted-foreground">Product sales</p>
            <div className="flex items-center gap-1 mt-1">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span className="text-xs text-green-400 font-medium">+5.43%</span>
            </div>
          </div>
          <div className="w-24 h-24">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={productStatsData}
                  cx="50%"
                  cy="50%"
                  innerRadius={25}
                  outerRadius={40}
                  dataKey="value"
                >
                  {productStatsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Monitor className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">Electronics</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">2,487</span>
              <span className="text-xs text-green-400">+1.8%</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gamepad2 className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">Games</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">1,828</span>
              <span className="text-xs text-green-400">+2.8%</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sofa className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">Furniture</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">1,463</span>
              <span className="text-xs text-red-400">-1.04%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const CustomerHabitsCard = () => (
    <Card className="bg-card border border-border col-span-2">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-semibold">Customer Habits</CardTitle>
          <p className="text-sm text-muted-foreground">Track your customer habbits</p>
        </div>
        <Button variant="outline" size="sm" className="text-xs">
          {selectedYear} ▼
        </Button>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={customerHabitsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="seenProduct" fill="#8B5CF6" name="Seen Product" />
              <Bar dataKey="sales" fill="#EC4899" name="Sales" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );

  const CustomerGrowthCard = () => (
    <Card className="bg-card border border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-semibold">Customer Growth</CardTitle>
          <p className="text-sm text-muted-foreground">Track your customer growth by location</p>
        </div>
        <Button variant="outline" size="sm" className="text-xs">
          Today ▼
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {customerGrowthData.map((country, index) => (
            <div key={country.country} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-lg">{country.flag}</span>
                <span className="text-sm font-medium">{country.country}</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-sm font-medium">{country.new}</div>
                  <div className="text-xs text-muted-foreground">New</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{country.returning}</div>
                  <div className="text-xs text-muted-foreground">Returning</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <div className="flex items-center justify-center h-full">Loading dashboard data...</div>;
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total sales"
          value={stats.total_sales}
          change={stats.sales_change}
          icon={DollarSign}
          isPositive={stats.sales_change.startsWith('+')}
          isPrimary={true}
        />
        <StatCard
          title="Total orders"
          value={stats.total_orders}
          change={stats.orders_change}
          icon={ShoppingCart}
          isPositive={stats.orders_change.startsWith('+')}
        />
        <StatCard
          title="Visitors"
          value={stats.total_visitors}
          change={stats.visitors_change}
          icon={Users}
          isPositive={stats.visitors_change.startsWith('+')}
        />
        <StatCard
          title="Total sold products"
          value={stats.total_sold_products}
          change={stats.products_change}
          icon={Package}
          isPositive={stats.products_change.startsWith('+')}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer Habits Chart */}
        <CustomerHabitsCard />
        
        {/* Product Statistics */}
        <ProductStatsCard />
      </div>

      {/* Customer Growth */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {/* This space can be used for additional charts or content */}
        </div>
        <CustomerGrowthCard />
      </div>
    </div>
  );
};

export default Dashboard;

