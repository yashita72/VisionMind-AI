import React, { useState, useEffect, useRef } from 'react';
import { 
  Eye, Shield, UserPlus, Image as ImageIcon, Users, FileText, Camera, Settings as SettingsIcon,
  Search, RefreshCw, CheckCircle, XCircle, AlertTriangle, Play, Pause, ChevronRight
} from 'lucide-react';

const API_BASE = window.location.origin.includes('3000') 
  ? 'http://localhost:8000' 
  : window.location.origin;

function App() {
  const [activeTab, setActiveTab] = useState('Home');
  const [threshold, setThreshold] = useState(0.363);
  const [attendance, setAttendance] = useState([]);
  const [stats, setStats] = useState({ registered: 0, logsToday: 0 });

  // Load stats and attendance logs
  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/attendance`);
      if (res.ok) {
        const data = await res.json();
        setAttendance(data);

        // Count unique names for registered count (as proxy)
        const uniqueNames = new Set(data.map(item => item.name));
        setStats({
          registered: uniqueNames.size || 3, // Fallback placeholder
          logsToday: data.length
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-[#0a0f1d] text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-[#111827]/80 backdrop-blur-md border-r border-slate-800 flex flex-col justify-between">
        <div>
          <div className="p-6 flex items-center space-x-3 border-b border-slate-800">
            <Eye className="w-8 h-8 text-blue-500 animate-pulse" />
            <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
              VisionMind AI
            </span>
          </div>

          <nav className="mt-6 px-4 space-y-1">
            {[
              { name: 'Home', icon: Users },
              { name: 'Face Detection', icon: ImageIcon },
              { name: 'Face Registration', icon: UserPlus },
              { name: 'Recognition & Verify', icon: Shield },
              { name: 'Search Face', icon: Search },
              { name: 'Live Camera', icon: Camera },
              { name: 'Attendance Logs', icon: FileText },
              { name: 'Settings', icon: SettingsIcon },
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.name}
                  onClick={() => setActiveTab(tab.name)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                    activeTab === tab.name
                      ? 'bg-blue-600/25 border-l-4 border-blue-500 text-blue-400 font-medium'
                      : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 flex justify-between">
          <span>Engine v1.0.0</span>
          <span className="text-emerald-500 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span> Online
          </span>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto bg-gradient-to-br from-[#0a0f1d] to-[#0f172a] p-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">{activeTab}</h1>
            <p className="text-slate-400 text-sm mt-1">Computer vision and recognition analytics dashboard</p>
          </div>
          <button 
            onClick={fetchLogs} 
            className="flex items-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-sm border border-slate-700 transition"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reload Data</span>
          </button>
        </header>

        {activeTab === 'Home' && <HomeView stats={stats} attendance={attendance} setActiveTab={setActiveTab} />}
        {activeTab === 'Face Detection' && <DetectionView />}
        {activeTab === 'Face Registration' && <RegistrationView />}
        {activeTab === 'Recognition & Verify' && <VerifyView />}
        {activeTab === 'Search Face' && <SearchView threshold={threshold} />}
        {activeTab === 'Live Camera' && <LiveCameraView threshold={threshold} />}
        {activeTab === 'Attendance Logs' && <AttendanceView attendance={attendance} />}
        {activeTab === 'Settings' && <SettingsView threshold={threshold} setThreshold={setThreshold} />}
      </main>
    </div>
  );
}

// 1. Home Dashboard View
function HomeView({ stats, attendance, setActiveTab }) {
  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800/40 border border-slate-800 backdrop-blur-md p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Identities Detected Today</span>
            <h3 className="text-4xl font-extrabold text-blue-500 mt-2">{stats.logsToday}</h3>
          </div>
          <Users className="w-12 h-12 text-blue-500/30" />
        </div>
        <div className="bg-slate-800/40 border border-slate-800 backdrop-blur-md p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Unique Database Profiles</span>
            <h3 className="text-4xl font-extrabold text-indigo-400 mt-2">{stats.registered}</h3>
          </div>
          <UserPlus className="w-12 h-12 text-indigo-400/30" />
        </div>
        <div className="bg-slate-800/40 border border-slate-800 backdrop-blur-md p-6 rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-slate-400 text-sm font-semibold uppercase tracking-wider">System State</span>
            <h3 className="text-4xl font-extrabold text-emerald-400 mt-2">Active</h3>
          </div>
          <Shield className="w-12 h-12 text-emerald-400/30" />
        </div>
      </div>

      {/* Recents */}
      <div className="bg-slate-800/30 border border-slate-800/80 backdrop-blur-md rounded-2xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h4 className="text-lg font-bold">Recent System Detections</h4>
          <button onClick={() => setActiveTab('Attendance Logs')} className="text-blue-400 hover:text-blue-300 text-sm flex items-center">
            <span>View All</span> <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        {attendance.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No detection logs found. Start the camera or upload an image.</p>
        ) : (
          <div className="space-y-3">
            {attendance.slice(0, 5).map((log) => (
              <div key={log.id} className="flex justify-between items-center bg-[#1e293b]/40 border border-slate-800 p-4 rounded-xl">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-blue-500/25 flex items-center justify-center font-bold text-blue-400">
                    {log.name[0]}
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-200">{log.name}</h5>
                    <span className="text-xs text-slate-500">{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-6">
                  <span className="text-sm font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full">
                    Match Confidence: {log.confidence.toLocaleString(undefined, { style: 'percent' })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 2. Face Detection Page
function DetectionView() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/detect`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Upload Box */}
      <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
        <form onSubmit={handleUpload} className="space-y-6">
          <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 transition-all rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center group">
            <ImageIcon className="w-12 h-12 text-slate-500 group-hover:text-blue-400 mb-4 transition" />
            <span className="font-bold text-slate-300">Select Face Image</span>
            <span className="text-xs text-slate-500 mt-1">PNG, JPG, JPEG</span>
            <input 
              type="file" 
              className="hidden" 
              accept="image/*"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setPreview(URL.createObjectURL(e.target.files[0]));
              }} 
            />
          </label>

          {preview && (
            <div className="mt-4 relative rounded-xl overflow-hidden border border-slate-700 bg-slate-900 max-h-80 flex items-center justify-center">
              <img src={preview} alt="Upload Preview" className="max-h-80 object-contain w-full" />
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl disabled:bg-slate-700 transition"
          >
            {loading ? 'Analyzing image...' : 'Run Face Detection'}
          </button>
        </form>
      </div>

      {/* Detection Results */}
      <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-lg font-bold mb-4">Detection Results</h3>
        {result ? (
          <div className="space-y-4">
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-xl font-medium">
              Faces Detected: {result.faces_detected}
            </div>

            <div className="space-y-3">
              {result.faces.map((face, index) => (
                <div key={index} className="bg-slate-900/60 p-4 border border-slate-800 rounded-xl space-y-2">
                  <div className="font-bold text-slate-300">Face {index + 1}</div>
                  <div className="text-xs text-slate-400">Bounding Box: {JSON.stringify(face.box)}</div>
                  <div className="text-xs text-slate-400">Landmarks confidence: {(face.score * 100).toFixed(2)}%</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-slate-500 py-12 text-center">Submit an image to run face detection and view landmarks.</p>
        )}
      </div>
    </div>
  );
}

// 3. Face Registration Page
function RegistrationView() {
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // { type: 'success'|'error', msg: string }

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!name || !file) return;
    setLoading(true);
    setStatus(null);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/register`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setStatus({ type: 'success', msg: data.message || 'User registered successfully!' });
        setName('');
        setFile(null);
        setPreview(null);
      } else {
        setStatus({ type: 'error', msg: data.detail || 'Registration failed.' });
      }
    } catch (err) {
      setStatus({ type: 'error', msg: 'A network error occurred.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto bg-slate-800/30 border border-slate-800 p-8 rounded-2xl">
      <h3 className="text-xl font-bold mb-6 text-center">Register New Identity</h3>

      {status && (
        <div className={`mb-6 p-4 rounded-xl border flex items-center space-x-3 ${
          status.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          {status.type === 'success' ? <CheckCircle className="w-6 h-6 flex-shrink-0" /> : <XCircle className="w-6 h-6 flex-shrink-0" />}
          <span>{status.msg}</span>
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-slate-400 mb-2">Full Name</label>
          <input 
            type="text" 
            placeholder="John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-[#111827]/70 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 text-slate-200"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-400 mb-2">Face Photograph</label>
          <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 transition-all rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center group bg-slate-900/30">
            <ImageIcon className="w-12 h-12 text-slate-500 group-hover:text-blue-400 mb-4 transition" />
            <span className="font-bold text-slate-300">Select Portrait Photo</span>
            <input 
              type="file" 
              className="hidden" 
              accept="image/*"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setPreview(URL.createObjectURL(e.target.files[0]));
              }}
              required
            />
          </label>
        </div>

        {preview && (
          <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-900 max-h-80 flex items-center justify-center">
            <img src={preview} alt="Upload Preview" className="max-h-80 object-contain w-full" />
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !name || !file}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl disabled:bg-slate-700 transition"
        >
          {loading ? 'Registering face...' : 'Complete Face Registration'}
        </button>
      </form>
    </div>
  );
}

// 4. Face Recognition Verification View
function VerifyView() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!file1 || !file2) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);

    try {
      const res = await fetch(`${API_BASE}/api/verify`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
      } else {
        alert(data.detail || 'Verification error');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleVerify} className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Photo 1 */}
        <div className="bg-slate-800/30 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <h4 className="font-bold text-slate-300">Photo A</h4>
          <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center bg-slate-900/30">
            <ImageIcon className="w-10 h-10 text-slate-500 mb-2" />
            <span className="text-sm font-semibold">Upload Photo A</span>
            <input type="file" className="hidden" accept="image/*" onChange={(e) => {
              setFile1(e.target.files[0]);
              setPreview1(URL.createObjectURL(e.target.files[0]));
            }} required />
          </label>
          {preview1 && <img src={preview1} className="h-48 object-contain rounded-xl border border-slate-850" />}
        </div>

        {/* Photo 2 */}
        <div className="bg-slate-800/30 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <h4 className="font-bold text-slate-300">Photo B</h4>
          <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center bg-slate-900/30">
            <ImageIcon className="w-10 h-10 text-slate-500 mb-2" />
            <span className="text-sm font-semibold">Upload Photo B</span>
            <input type="file" className="hidden" accept="image/*" onChange={(e) => {
              setFile2(e.target.files[0]);
              setPreview2(URL.createObjectURL(e.target.files[0]));
            }} required />
          </label>
          {preview2 && <img src={preview2} className="h-48 object-contain rounded-xl border border-slate-850" />}
        </div>

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={loading || !file1 || !file2}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl disabled:bg-slate-700 transition"
          >
            {loading ? 'Comparing profiles...' : 'Verify Same Person'}
          </button>
        </div>
      </form>

      {result && (
        <div className={`p-6 rounded-2xl border flex items-center justify-between ${
          result.verified 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          <div className="flex items-center space-x-4">
            {result.verified ? <CheckCircle className="w-12 h-12" /> : <XCircle className="w-12 h-12" />}
            <div>
              <h4 className="text-xl font-bold">{result.verified ? 'Verified Match' : 'Mismatch'}</h4>
              <p className="text-sm opacity-80 mt-1">Similarity Score: {result.similarity_score.toFixed(4)}</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-2xl font-black">{result.confidence.toLocaleString(undefined, { style: 'percent' })}</span>
            <p className="text-xs uppercase tracking-wider opacity-60 mt-1">Confidence</p>
          </div>
        </div>
      )}
    </div>
  );
}

// 5. Face Search View
function SearchView({ threshold }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/search?threshold=${threshold}`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.matches);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Upload */}
      <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
        <form onSubmit={handleSearch} className="space-y-6">
          <label className="border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center bg-slate-900/30">
            <ImageIcon className="w-12 h-12 text-slate-500 mb-4" />
            <span className="font-bold text-slate-300">Select Unknown Face</span>
            <input type="file" className="hidden" accept="image/*" onChange={(e) => {
              setFile(e.target.files[0]);
              setPreview(URL.createObjectURL(e.target.files[0]));
            }} required />
          </label>

          {preview && (
            <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-slate-900 max-h-80 flex items-center justify-center">
              <img src={preview} alt="Upload Preview" className="max-h-80 object-contain w-full" />
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl disabled:bg-slate-700 transition"
          >
            {loading ? 'Searching database...' : 'Search Matching Identities'}
          </button>
        </form>
      </div>

      {/* Results */}
      <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-lg font-bold mb-4">Database Matches (Top-5)</h3>
        {results ? (
          <div className="space-y-3">
            {results.length === 0 ? (
              <p className="text-slate-500 py-12 text-center">No matches found matching search threshold.</p>
            ) : (
              results.map((match, idx) => (
                <div key={idx} className={`p-4 rounded-xl border flex justify-between items-center ${
                  match.is_match 
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                    : 'bg-slate-900 border-slate-850 text-slate-400'
                }`}>
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-xs opacity-60">#{idx + 1}</span>
                    <div>
                      <h5 className="font-bold">{match.name}</h5>
                      <span className="text-xs opacity-60">Cosine Score: {match.similarity_score.toFixed(4)}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-bold">{match.confidence.toLocaleString(undefined, { style: 'percent' })}</span>
                    <p className="text-[10px] uppercase tracking-wider opacity-60">Confidence</p>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <p className="text-slate-500 py-12 text-center">Upload an unknown portrait to query the registered database.</p>
        )}
      </div>
    </div>
  );
}

// 6. Live Camera View
function LiveCameraView({ threshold }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [streamActive, setStreamActive] = useState(false);
  const [currentMatch, setCurrentMatch] = useState(null);
  const intervalRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreamActive(true);
        startRecognitionLoop();
      }
    } catch (e) {
      alert('Camera access denied or unavailable.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setStreamActive(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setCurrentMatch(null);
  };

  const startRecognitionLoop = () => {
    intervalRef.current = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob/file to upload
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        try {
          const res = await fetch(`${API_BASE}/api/search?threshold=${threshold}`, {
            method: 'POST',
            body: formData
          });
          if (res.ok) {
            const data = await res.json();
            if (data.matches && data.matches.length > 0) {
              const bestMatch = data.matches[0];
              setCurrentMatch(bestMatch);
            } else {
              setCurrentMatch(null);
            }
          }
        } catch (err) {
          console.error(err);
        }
      }, 'image/jpeg');
    }, 1000); // Poll database matching every 1 second
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Video Feed */}
      <div className="lg:col-span-2 bg-slate-800/30 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between space-y-4">
        <div className="relative rounded-2xl overflow-hidden border border-slate-700 bg-slate-900 aspect-video flex items-center justify-center">
          <video ref={videoRef} className="w-full h-full object-cover hidden" />
          <canvas ref={canvasRef} width="640" height="480" className={`w-full h-full object-cover ${streamActive ? 'block' : 'hidden'}`} />
          {!streamActive && (
            <div className="text-center p-8">
              <Camera className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-bounce" />
              <span className="text-slate-400 block font-semibold">Webcam Feed Inactive</span>
            </div>
          )}
        </div>

        <div className="flex space-x-4">
          {!streamActive ? (
            <button onClick={startCamera} className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition">
              <Play className="w-5 h-5" />
              <span>Start Webcam Feed</span>
            </button>
          ) : (
            <button onClick={stopCamera} className="flex-1 flex items-center justify-center space-x-2 bg-rose-600 hover:bg-rose-500 py-3 rounded-xl font-bold transition">
              <Pause className="w-5 h-5" />
              <span>Stop Webcam Feed</span>
            </button>
          )}
        </div>
      </div>

      {/* Matching State */}
      <div className="bg-slate-800/30 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-lg font-bold mb-6">Real-Time Recognition Result</h3>
        {streamActive ? (
          currentMatch ? (
            currentMatch.is_match ? (
              <div className="bg-emerald-500/10 border border-emerald-500/30 p-6 rounded-2xl text-center space-y-4">
                <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto" />
                <div>
                  <h4 className="text-2xl font-black text-emerald-400">{currentMatch.name}</h4>
                  <span className="text-xs text-emerald-500 font-semibold block mt-1">Status: REGISTERED PROFILE</span>
                </div>
                <div className="text-3xl font-extrabold text-slate-200">
                  {currentMatch.confidence.toLocaleString(undefined, { style: 'percent' })}
                </div>
                <span className="text-xs opacity-60 block">Confidence Score</span>
              </div>
            ) : (
              <div className="bg-rose-500/10 border border-rose-500/30 p-6 rounded-2xl text-center space-y-4">
                <AlertTriangle className="w-16 h-16 text-rose-400 mx-auto" />
                <div>
                  <h4 className="text-2xl font-black text-rose-400">Unknown Person</h4>
                  <span className="text-xs text-rose-500 font-semibold block mt-1">Status: UNKNOWN IDENTITY</span>
                </div>
                <p className="text-sm text-slate-400 px-4">Face detected, but resemblance is below search match threshold ({threshold}).</p>
              </div>
            )
          ) : (
            <div className="text-center py-12">
              <RefreshCw className="w-12 h-12 text-slate-500 mx-auto animate-spin mb-4" />
              <p className="text-slate-400">Analyzing camera feed frames...</p>
            </div>
          )
        ) : (
          <p className="text-slate-500 py-12 text-center">Activate the webcam feed to test live recognition.</p>
        )}
      </div>
    </div>
  );
}

// 7. Attendance Log View
function AttendanceView({ attendance }) {
  return (
    <div className="bg-slate-800/30 border border-slate-800 rounded-2xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-[#1e293b]/55 text-slate-400 text-xs font-semibold uppercase tracking-wider">
              <th className="py-4 px-6">ID</th>
              <th className="py-4 px-6">Name</th>
              <th className="py-4 px-6">Timestamp</th>
              <th className="py-4 px-6">Confidence</th>
              <th className="py-4 px-6">Screenshot</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {attendance.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center py-12 text-slate-500">No logs stored yet.</td>
              </tr>
            ) : (
              attendance.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/10 text-sm">
                  <td className="py-4 px-6 font-mono text-xs text-slate-500">#{log.id}</td>
                  <td className="py-4 px-6 font-bold text-slate-200">{log.name}</td>
                  <td className="py-4 px-6 text-slate-400">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="py-4 px-6">
                    <span className="text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full font-medium text-xs">
                      {log.confidence.toLocaleString(undefined, { style: 'percent' })}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <a 
                      href={`${API_BASE}/${log.screenshot_path}`} 
                      target="_blank" 
                      rel="noreferrer"
                      className="text-blue-400 hover:text-blue-300 font-semibold"
                    >
                      View Photo
                    </a>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// 8. Settings View
function SettingsView({ threshold, setThreshold }) {
  return (
    <div className="max-w-xl mx-auto bg-slate-800/30 border border-slate-800 p-8 rounded-2xl space-y-6">
      <h3 className="text-xl font-bold border-b border-slate-800 pb-4">Verification Settings</h3>
      
      <div className="space-y-4">
        <label className="block text-sm font-semibold text-slate-300">Similarity Match Threshold</label>
        <p className="text-xs text-slate-500">
          Set the cosine similarity score above which a detected face is recognized as a known profile. Default: 0.363 (standard SFace recommendation).
        </p>
        <div className="flex items-center space-x-4">
          <input 
            type="range" 
            min="0.0" 
            max="1.0" 
            step="0.01" 
            value={threshold} 
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="flex-1 accent-blue-500"
          />
          <span className="font-mono bg-slate-900 border border-slate-800 px-3 py-2 rounded-xl text-blue-400 font-bold w-16 text-center">
            {threshold}
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;
