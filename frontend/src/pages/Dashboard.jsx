
import { useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Sprout, Calendar, Loader2, MapPin, IndianRupee, LogOut } from 'lucide-react'

export default function Dashboard({ setToken }) {
    const [location, setLocation] = useState('Bengaluru')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [showHistory, setShowHistory] = useState(false)
    const [history, setHistory] = useState([])

    const handleLogout = () => {
        setToken(null)
        localStorage.removeItem('token')
    }

    const fetchHistory = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get('/api/history', {
                headers: { Authorization: `Bearer ${token}` }
            })
            setHistory(response.data)
            setShowHistory(true)
        } catch (err) {
            console.error(err)
            setError('Failed to fetch history')
        }
    }

    const handleRecommend = async () => {
        setLoading(true)
        setError(null)
        setResult(null)
        setShowHistory(false)
        try {
            const token = localStorage.getItem('token')
            const response = await axios.post('/api/recommend',
                { location },
                { headers: { Authorization: `Bearer ${token}` } }
            )
            setResult(response.data)
        } catch (err) {
            console.error(err)
            setError(err.response?.data?.error || 'Failed to fetch recommendations. Ensure backend is running.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-slate-900 text-white font-sans selection:bg-green-500 selection:text-white">
            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-green-500/10 blur-[100px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[100px]" />
            </div>

            <nav className="relative z-10 flex justify-end p-4 gap-4">
                <button
                    onClick={() => { setShowHistory(false); setResult(null); }}
                    className={`text-sm font-medium transition-colors ${!showHistory && !result ? 'text-green-400' : 'text-slate-400 hover:text-white'}`}
                >
                    New Search
                </button>
                <button
                    onClick={fetchHistory}
                    className={`text-sm font-medium transition-colors ${showHistory ? 'text-green-400' : 'text-slate-400 hover:text-white'}`}
                >
                    History
                </button>
                <div className="w-px h-5 bg-slate-700 my-auto"></div>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium"
                >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                </button>
            </nav>

            <main className="relative container mx-auto px-4 py-8 max-w-4xl">
                {/* Header */}
                <div className="text-center mb-16 space-y-4">
                    <div className="inline-flex items-center justify-center p-3 bg-green-500/10 rounded-2xl mb-4 ring-1 ring-green-500/20">
                        <Sprout className="w-8 h-8 text-green-400" />
                    </div>
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500 pb-2">
                        Cocoon Cycle Optimizer
                    </h1>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        AI-powered scheduling for optimal silk cocoon rearing. Maximize your yield and profit with precision timing.
                    </p>
                </div>

                {showHistory ? (
                    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <span className="w-2 h-8 bg-green-500 rounded-full"></span>
                            Your Search History
                        </h2>
                        {history.length === 0 ? (
                            <div className="text-slate-500 text-center py-12">No history found. Start searching!</div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-slate-700 text-slate-400 text-sm uppercase tracking-wider">
                                            <th className="p-4 font-medium">Date Searched</th>
                                            <th className="p-4 font-medium">Location</th>
                                            <th className="p-4 font-medium">Start Date</th>
                                            <th className="p-4 font-medium">Harvest Date</th>
                                            <th className="p-4 font-medium text-right">Proj. Price</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-700/50">
                                        {history.map((item) => (
                                            <tr key={item.id} className="hover:bg-slate-700/20 transition-colors">
                                                <td className="p-4 text-slate-400">{item.created_at}</td>
                                                <td className="p-4 font-medium text-white">{item.location}</td>
                                                <td className="p-4 text-green-400">{item.start_date}</td>
                                                <td className="p-4 text-blue-400">{item.harvest_date}</td>
                                                <td className="p-4 text-right font-bold text-yellow-400">₹{Math.round(item.predicted_price)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                ) : (
                    <>
                        {/* Control Panel */}
                        <div className="grid md:grid-cols-2 gap-8 mb-12">
                            <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
                                {/* Hover glow */}
                                <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                                    <MapPin className="w-5 h-5 text-blue-400" />
                                    Select Location
                                </h2>

                                <div className="space-y-6 relative z-10">
                                    <div className="space-y-2">
                                        <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Region</label>
                                        <select
                                            value={location}
                                            onChange={(e) => setLocation(e.target.value)}
                                            className="w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-all text-lg appearance-none cursor-pointer hover:bg-slate-900/80"
                                        >
                                            <option value="Bengaluru">Bengaluru</option>
                                            <option value="Ramanagara">Ramanagara</option>
                                            <option value="Siddlaghatta">Siddlaghatta</option>
                                        </select>
                                    </div>

                                    <button
                                        onClick={handleRecommend}
                                        disabled={loading}
                                        className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-green-500/20 transform transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                    >
                                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Calendar className="w-5 h-5" />}
                                        {loading ? 'Analyzing...' : 'Find Best Start Date'}
                                    </button>
                                </div>
                            </div>

                            {/* Result Card */}
                            <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl relative flex flex-col justify-center items-center text-center min-h-[300px]">
                                {!result && !loading && !error && (
                                    <div className="text-slate-500 text-sm">
                                        <Sprout className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                        Select a location and click the button to see recommendations.
                                    </div>
                                )}

                                {error && (
                                    <div className="text-red-400 p-4 bg-red-500/10 rounded-xl border border-red-500/20">
                                        {error}
                                    </div>
                                )}

                                {result && (
                                    <div className="animate-in fade-in zoom-in duration-500 space-y-6 w-full">
                                        <div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Recommended Start</div>
                                                    <div className="text-3xl font-bold text-white tracking-tight">{result.recommended_date}</div>
                                                </div>
                                                <div className="text-right border-l border-slate-700/50 pl-4">
                                                    <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Expected Harvest</div>
                                                    <div className="text-3xl font-bold text-green-400 tracking-tight">{result.expected_harvest_date}</div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent w-full" />

                                        <div>
                                            <div className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">Projected Price at Harvest</div>
                                            <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-b from-yellow-300 to-yellow-500 flex items-center justify-center gap-1">
                                                <IndianRupee className="w-8 h-8 text-yellow-400" strokeWidth={3} />
                                                {Math.round(result.predicted_price)}
                                            </div>
                                            <div className="text-xs text-slate-500 mt-2">Predicted for {result.expected_harvest_date}</div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}

                {/* Chart Section - Only show if we have data */}
                {result?.all_predictions && (
                    <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-in slide-in-from-bottom-10 fade-in duration-700 delay-100">
                        <h3 className="text-xl font-semibold mb-6 text-slate-200">Price Trend by Start Date</h3>
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                {/* Sort predictions by date for the chart to show Day 1 -> Day 10 progress */}
                                <LineChart data={[...result.all_predictions].sort((a, b) => new Date(a.start_date) - new Date(b.start_date))}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                    <XAxis
                                        dataKey="start_date"
                                        tickFormatter={(val, index) => `Day ${index + 1}`}
                                        stroke="#94a3b8"
                                        interval={0}
                                    />
                                    <YAxis
                                        stroke="#94a3b8"
                                        tickFormatter={(val) => `₹${val}`}
                                        domain={['auto', 'auto']}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '12px', color: '#f8fafc' }}
                                        itemStyle={{ color: '#fbbf24' }}
                                        labelStyle={{ color: '#94a3b8', marginBottom: '0.5rem' }}
                                        formatter={(value) => [`₹${Math.round(value)}`, 'Harvest Price']}
                                        labelFormatter={(label, payload) => {
                                            if (payload && payload.length > 0) {
                                                const data = payload[0].payload;
                                                return `Start: ${data.start_date} → Harvest: ${data.harvest_date}`;
                                            }
                                            return `Start Date: ${label}`;
                                        }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="predicted_price"
                                        stroke="#10b981"
                                        strokeWidth={3}
                                        dot={true}
                                        activeDot={{ r: 6, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}
