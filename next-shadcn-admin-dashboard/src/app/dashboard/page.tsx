"use client";

import { useEffect, useState } from "react";

import { Avatar, AvatarFallback } from "@radix-ui/react-avatar";
import initials from "initials";
import { DollarSign, Users, CreditCard, Activity } from "lucide-react";
import { DateRange } from "react-day-picker";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

import { DateRangePicker } from "@/components/DateRangePicker";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { salesData, overviewChartData } from "@/constants/dummyData";
interface Balance {
  asset: string;
  free: number;
  locked: number;
}
import { Table, TableHeader, TableBody } from "@/components/ui/table";

interface WebSocketContextType {
  balances: Balance[];
}

export default function Page() {
  const [selectedRange, setSelectedRange] = useState<DateRange | undefined>(undefined);
  const [balances, setBalances] = useState<Balance[]>([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws`);
    console.log(process.env.NEXT_PUBLIC_WS_URL);
    ws.onmessage = (event) => {
      console.log(event.data);
      const data = JSON.parse(event.data);
      setBalances(data);
    };
    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="flex-col md:flex">
      <div className="flex-1 space-y-4">
        <div className="flex-col items-center justify-between space-y-2 md:flex md:flex-row">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <div className="flex-col items-center space-y-2 md:flex md:flex-row md:space-x-2 md:space-y-0">
            <DateRangePicker selectedRange={selectedRange} onChangeRange={setSelectedRange} />
            <Button className="w-full">Download</Button>
          </div>
        </div>
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics" disabled>
              Analytics
            </TabsTrigger>
            <TabsTrigger value="reports" disabled>
              Reports
            </TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                  <DollarSign className="size-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$45,231.89</div>
                  <p className="text-xs text-muted-foreground">+20.1% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Subscriptions</CardTitle>
                  <Users className="size-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+2350</div>
                  <p className="text-xs text-muted-foreground">+180.1% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Sales</CardTitle>
                  <CreditCard className="size-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+12,234</div>
                  <p className="text-xs text-muted-foreground">+19% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Now</CardTitle>
                  <Activity className="size-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">+573</div>
                  <p className="text-xs text-muted-foreground">+201 since last hour</p>
                </CardContent>
              </Card>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              {/* <Card className="col-span-2 lg:col-span-4">
                <CardHeader>
                  <CardTitle>Overview</CardTitle>
                </CardHeader>
                <CardContent className="pl-2">
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={overviewChartData}>
                      <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis
                        stroke="#888888"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `$${value}`}
                      />
                      <Bar dataKey="total" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card> */}
              <Card className="col-span-4 lg:col-span-12">
                <CardHeader>
                  <CardTitle>Asset Balances</CardTitle>
                  <CardDescription>Real-time balance updates in USDT</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <tr>
                        <th className="text-left">Asset</th>
                        <th className="text-right">Free</th>
                        <th className="text-right">Locked</th>
                      </tr>
                    </TableHeader>
                    <TableBody>
                      {balances.map((balance) => (
                        <tr key={balance.asset}>
                          <td className="font-medium">{balance.asset}</td>
                          <td className="text-right">{balance.free.toFixed(4)}</td>
                          <td className="text-right">{balance.locked.toFixed(4)}</td>
                        </tr>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
