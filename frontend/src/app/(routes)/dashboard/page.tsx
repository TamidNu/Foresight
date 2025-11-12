"use client";

import React from "react";
import ProgressBar from "../../../components/progress-bar";
import type { Metadata } from "next";
import { useUser } from "@clerk/nextjs";
import { PricingItem, PricingResponse } from "@/types/pricing";
import { quote, QuoteParams } from "@/services/pricingService"
import { PricingTable } from "@/components/pricing-table";
import { handleUserSignup } from "@/services/userService";

/**export const metadata: Metadata = {
  title: "Dashboard",
  description:
    "Description here",
  openGraph: {
    title: "Dashboard | Foresight",
    description:
      "Description here",
    url: "https://foresight-tamid.vercel.app/dashboard",
    siteName: "Foresight",
  }
};**/

function Dashboard() {
  const { user, isLoaded } = useUser();
  
  const [pricingItems, setPricingItems] = React.useState<PricingItem[]>([]);
  const [loading, setLoading] = React.useState(true);

React.useEffect(() => {
  if (!user || !isLoaded) return;

  handleUserSignup(user);
}, [user, isLoaded]);


  const today = new Date();
  const to = new Date();
  to.setDate(today.getDate() + 30);
  const format = (d: Date) => d.toISOString().slice(0, 10);

  const pricingPayload: QuoteParams = {
    hotel_id: 1,
    room_type_code: "DLX-QUEEN",
    from_: format(today),
    to: format(to),
  };

  React.useEffect(() => {
  async function fetchPricing() {
    try {
      const pricingData: PricingResponse = await quote(pricingPayload);
      setPricingItems(pricingData.items);
    } catch (err) {
      console.error("Failed to fetch pricing", err);
    } finally {
      setLoading(false);
    }
  }

  fetchPricing();
 }, []);


  const textColor = "text-[#013172]";
  const borderColor = "border-[#D1D5DB]";
  const fontClass = "font-sans";

  return (
    <div className={`flex flex-1 ${textColor}`}>
      <aside className={`w-72 bg-white border-r ${borderColor} p-4 space-y-4`}>
        <div>
          <p className="text-med mb-2">Date</p>
          <h2 className="font-bold">Property Name</h2>
          <p className="text-med text-[#4981d6] mb-2">Name</p>
        </div>
        <div>
          <p className="font-semibold">Occupancy (Next 7 Days)</p>
          <p className="text-xl text-[#4981d6] mb-2">{90}%</p>
          <ProgressBar progress={90} />
        </div>
        <div>
          <p className="font-semibold">Revenue (MTD)</p>
          <p className="text-xl text-[#4981d6] mb-2">$0</p>
        </div>
        <div>
          <p className="font-semibold">Active Alerts</p>
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-2 mb-2">
            <p className="text-sm">Event</p>
          </div>
          <div className="bg-red-100 border-l-4 border-red-500 p-2 mb-2">
            <p className="text-sm">Event</p>
          </div>
          <div className="bg-green-100 border-l-4 border-green-500 p-2 mb-2">
            <p className="text-sm">Event</p>
          </div>
        </div>
      </aside>
      <main className="flex-1 p-6 space-y-6">
        <h1 className="text-xl font-bold">Revenue Command Center</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className={`bg-[#e8f1ff] border border-[#aecaf5] rounded shadow`}>
            <div className="p-4">
              <p className="text-med text-gray-500">Incremental Revenue</p>
            </div>
          </div>
          <div className={`bg-[#e8f1ff] border border-[#aecaf5] rounded shadow`}>
            <div className="p-4">
              <p className="text-med text-gray-500">Intelligence Signals</p>
            </div>
          </div>
        </div>
        <div className={`bg-white border ${borderColor} rounded shadow`}>
          <div className="p-4">
            <p className="font-semibold">Revenue Performance</p>
            <div className="h-20 bg-gray-100 flex items-center justify-center text-gray-400">
              Chart
            </div>
          </div>
        </div>
        <div className={`bg-white border ${borderColor} rounded shadow`}>
          <div className="p-4">
            <p className="font-semibold">Demand Forecast (Next 30 Days)</p>
            <div className="h-32 flex items-center justify-left mb-4">
              {loading ? <p>Loading pricing...</p> : <PricingTable items={pricingItems} />}
            </div>
            <button className="bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300 text-white px-4 py-2 rounded">
              Export as CSV
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
