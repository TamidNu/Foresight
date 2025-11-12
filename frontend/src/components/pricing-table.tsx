import type { PricingItem } from "@/types/pricing";

interface PricingTableProps {
    items: PricingItem[];
}

export function PricingTable({ items, loading, error }: { items: PricingItem[], loading: boolean, error?: Error }) {
  if (error) {
    console.error(error)
    return <p className="text-red-500">Couldn't load recommendations. Please try again.</p>;
  }
  
  if (loading) {
    <div className="flex justify-center items-center p-4">
        <p>Loading...</p>
    </div>
  }
  
  if (items.length == 0) {
    return <p className="text-gray-400">No pricing recommendations available.</p>
  }
  
  
  return (
    <div className="max-w-4xl h-35 overflow-auto border rounded shadow"> 
        <table className="min-w-full border border-gray-300">
      <thead className="bg-gray-100">
        <tr>
          <th className="px-4 py-2 border">Date</th>
          <th className="px-4 py-2 border">Recommended Price</th>
          <th className="px-4 py-2 border">Min</th>
          <th className="px-4 py-2 border">Max</th>
          <th className="px-4 py-2 border">Notes</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.date}>
            <td className="px-4 py-2 border">{item.date}</td>
            <td className="px-4 py-2 border">{item.price_rec.toFixed(2)}</td>
            <td className="px-4 py-2 border">{item.price_min.toFixed(2)}</td>
            <td className="px-4 py-2 border">{item.price_max.toFixed(2)}</td>
            <td className="px-4 py-2 border">{item.drivers.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
    );
}