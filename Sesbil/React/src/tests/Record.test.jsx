import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom' 
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Histogram from '../pages/record/components/Histogram'
import ControlButtons from '../pages/record/components/ControlButtons'
import PieChart from '../pages/record/components/PieChart'
import Results from '../pages/record/components/Results'
import Record from '../pages/record/Record' 

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Histogram
test('imgData verildiğinde img render edilir', () => {
  const fakeImg = 'data:image/png;base64,fake-image-data'
  render(<Histogram imgData={fakeImg} />)
  const image = screen.getByRole('img')
  expect(image).toBeInTheDocument()
  expect(image).toHaveAttribute('src', fakeImg)
})

test('imgData null olduğunda img görünmez', () => {
  render(<Histogram imgData={null} />)
  const image = screen.queryByRole('img')
  expect(image).not.toBeInTheDocument()
})

// ControlButtons
test('ilk ekranda Başla ve Ses Kaydet butonları görünür', () => {
  render(
    <MemoryRouter>
      <ControlButtons onStart={vi.fn()} onStop={vi.fn()} />
    </MemoryRouter>
  )
  expect(screen.getByText('Başla')).toBeInTheDocument()
  expect(screen.getByText('Ses Kaydet')).toBeInTheDocument()
})

test('Başla butonuna tıklanınca onStart çalışır ve Durdur butonu görünür', () => {
  const onStartMock = vi.fn()
  render(
    <MemoryRouter>
      <ControlButtons onStart={onStartMock} onStop={vi.fn()} />
    </MemoryRouter>
  )
  fireEvent.click(screen.getByText('Başla'))
  expect(onStartMock).toHaveBeenCalledTimes(1)
  expect(screen.getByText('Durdur')).toBeInTheDocument()
})

test('Durdur butonuna tıklanınca onStop çalışır', () => {
  const onStartMock = vi.fn()
  const onStopMock = vi.fn()
  render(
    <MemoryRouter>
      <ControlButtons onStart={onStartMock} onStop={onStopMock} />
    </MemoryRouter>
  )
  fireEvent.click(screen.getByText('Başla'))
  fireEvent.click(screen.getByText('Durdur'))
  expect(onStopMock).toHaveBeenCalledTimes(1)
})

test('Ses Kaydet butonuna tıklanırsa navigate çağrılır', () => {
  render(
    <MemoryRouter>
      <ControlButtons onStart={vi.fn()} onStop={vi.fn()} />
    </MemoryRouter>
  )
  fireEvent.click(screen.getByText('Ses Kaydet'))
  expect(mockNavigate).toHaveBeenCalledWith('/recordDatabase')
})

// Results
const emptyData = {
  kisi: "Ali",
  konusanlar: "Ali:20s, Veli:10s",
  metin: "",
  konu: "",
  duygu: ""
}

const fullData = {
  kisi: "Ali",
  konusanlar: "Ali:20s, Veli:10s",
  metin: "Bu bir testtir.",
  konu: "Spor:70%, Sağlık:30%",
  duygu: "Mutlu"
}

test('Metin boşsa sadece kişi ve konuşanlar gösterilir', () => {
  render(<Results data={emptyData} />)
  expect(screen.getByText(/Konuşan kişi:/)).toBeInTheDocument()
  expect(screen.getByText(/Konuşanlar:/)).toBeInTheDocument()
  expect(screen.queryByText(/Duygu Durumu/)).not.toBeInTheDocument()
})

test('Metin varsa PieChart ve duygu gösterilir', () => {
  render(<Results data={fullData} />)
  expect(screen.getByText(/Konuşulan Metin:/)).toBeInTheDocument()
  expect(screen.getByText(/Duygu Durumu: Mutlu/)).toBeInTheDocument()
  const emotionImg = document.querySelector('img')
  expect(emotionImg).toBeInTheDocument()
})

// Record 
global.fetch = vi.fn(() => Promise.resolve({ json: () => Promise.resolve({}) }))

class FakeWebSocket {
  constructor() {
    this.onmessage = null
    this.onclose = null
    this.readyState = WebSocket.OPEN
  }
  send() {}
  close() {
    if (this.onclose) this.onclose()
  }
  simulateMessage(msg) {
    if (this.onmessage) this.onmessage({ data: msg })
  }
}
global.WebSocket = vi.fn(() => new FakeWebSocket())

describe("Record Bileşeni", () => {
  test("Başlangıçta reset fetch çağrısı yapılmalı", async () => {
    render(<Record />)
    expect(fetch).toHaveBeenCalledWith('http://localhost:5020/api/recording/reset', { method: 'POST' })
  })

  test("Başla butonuna basınca start fetch çağrılır ve WebSocket bağlanır", async () => {
    render(<Record />)
    const startBtn = screen.getByRole("button", { name: "Başla" })
    fireEvent.click(startBtn)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:5020/api/recording/start', { method: 'POST' })
      expect(global.WebSocket).toHaveBeenCalledWith("ws://127.0.0.1:8000/information")
    })
  })

  test("WebSocket'ten gelen mesaj veriyi günceller", async () => {
    render(<Record />)
    const ws = new FakeWebSocket()
    global.WebSocket.mockImplementationOnce(() => ws)
    const startBtn = screen.getByRole("button", { name: "Başla" })
    fireEvent.click(startBtn)
    await waitFor(() => expect(fetch).toHaveBeenCalledWith('http://localhost:5020/api/recording/start', { method: 'POST' }))
    ws.simulateMessage("ilk mesajSelam dünya")
    await waitFor(() => expect(screen.getByText(/Konuşulan Metin:/)).toBeInTheDocument())
    expect(screen.getByText(/Selam dünya/)).toBeInTheDocument()
  })

  test("Durdur butonuna basınca stop fetch çağrılır", async () => {
    render(<Record />)
    const startBtn = screen.getByRole("button", { name: "Başla" })
    fireEvent.click(startBtn)
    const stopBtn = await screen.findByRole("button", { name: "Durdur" })
    fireEvent.click(stopBtn)
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:5020/api/recording/stop', { method: 'POST' })
    })
  })
})
