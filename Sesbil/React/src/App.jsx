import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Record from './pages/record/Record.jsx';
import RecordDatabase from './pages/recordDatabase/RecordDatabase.jsx';
import Header from './pages/shared/Header.jsx';
import './app.css'

export default function App() {
  return (
    <Header>
      <main className="main-content">
      <Routes>
        <Route path="/" element={<Record />} />
        <Route path="/recordDatabase" element={<RecordDatabase />} />
      </Routes>
      </main>
    </Header>
  )
}