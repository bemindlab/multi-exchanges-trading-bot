import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Button } from "./ui/button";

const Dashboard = () => {
  const [bots, setBots] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchBots = async () => {
      try {
        const response = await axios.get("http://localhost:8000/bots", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setBots(response.data);
      } catch (error) {
        console.error("Error fetching bots:", error);
        if (error.response?.status === 401) {
          navigate("/login");
        }
      }
    };

    fetchBots();
    const interval = setInterval(fetchBots, 5000);
    return () => clearInterval(interval);
  }, [navigate]);

  const handleStartBot = async (botId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`http://localhost:8000/bots/${botId}/start`, null, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const response = await axios.get("http://localhost:8000/bots", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setBots(response.data);
    } catch (error) {
      console.error("Error starting bot:", error);
    }
  };

  const handleStopBot = async (botId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`http://localhost:8000/bots/${botId}/stop`, null, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const response = await axios.get("http://localhost:8000/bots", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setBots(response.data);
    } catch (error) {
      console.error("Error stopping bot:", error);
    }
  };

  const performanceData = [
    { time: "00:00", profit: 0 },
    { time: "01:00", profit: 50 },
    { time: "02:00", profit: 75 },
    { time: "03:00", profit: 100 },
    { time: "04:00", profit: 80 },
    { time: "05:00", profit: 120 },
  ];

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="bg-card rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">
          Overall Performance
        </h2>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="profit"
                stroke="hsl(var(--primary))"
                name="Profit"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {bots.map((bot) => (
          <div
            key={bot.bot_id}
            className="bg-card rounded-lg shadow-lg p-6 space-y-4"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Bot {bot.bot_id}
                </h3>
                <p className="text-muted-foreground">Status: {bot.status}</p>
              </div>
              {bot.status === "stopped" ? (
                <Button
                  onClick={() => handleStartBot(bot.bot_id)}
                  variant="default"
                >
                  Start Bot
                </Button>
              ) : (
                <Button
                  onClick={() => handleStopBot(bot.bot_id)}
                  variant="destructive"
                >
                  Stop Bot
                </Button>
              )}
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Last Update: {new Date(bot.last_update).toLocaleString()}
              </p>
              <p className="text-sm text-muted-foreground">
                Profit: {bot.performance.profit}
              </p>
              <p className="text-sm text-muted-foreground">
                Total Trades: {bot.performance.trades}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
