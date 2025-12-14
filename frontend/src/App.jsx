import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    axios.get('http://localhost:6543/api/reviews')
      .then(res => setReviews(res.data))
      .catch(err => console.error(err))
  }, [])

  const handleAnalyze = async () => {
    if (!text) return
    setLoading(true)
    try {
      const res = await axios.post('http://localhost:6543/api/analyze-review', { text })
      setReviews([res.data, ...reviews])
      setText('')
    } catch (err) {
      alert("Backend Error! Pastikan Python menyala.")
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>Product Review Analyzer</h1>
      <div className="input-box">
        <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Tulis review... (contoh: Laptop ini bagus)" />
        <button onClick={handleAnalyze} disabled={loading}>{loading ? 'Analyzing...' : 'Analyze'}</button>
      </div>
      <div className="list">
        {reviews.map(r => (
          <div key={r.id} className="card">
            <div className={`badge ${r.sentiment.label}`}>{r.sentiment.label} ({r.sentiment.score})</div>
            <p>"{r.text}"</p>
            <div className="insight"><pre>{r.key_points}</pre></div>
          </div>
        ))}
      </div>
    </div>
  )
}
export default App