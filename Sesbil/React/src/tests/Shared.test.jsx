import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom' 
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Header from '../pages/shared/Header' 
import Instructions from '../pages/shared/Instructions' 

describe('Header bileşeni', () => {
  test('Logo resmi render edilir ve alt metin doğru', () => {
    render(<Header />)
    const img = screen.getByAltText('resim bulunamadı')
    expect(img).toBeInTheDocument()
    expect(img.getAttribute('src')).toContain('sesbil_logo.png')
    expect(img).toHaveAttribute('height', '240px')
    expect(img).toHaveAttribute('width', '270px')
  })

  test('children render edilir', () => {
    render(
      <Header>
        <div data-testid="child-element">Çocuk İçerik</div>
      </Header>
    )
    expect(screen.getByTestId('child-element')).toBeInTheDocument()
    expect(screen.getByText('Çocuk İçerik')).toBeInTheDocument()
  })
})

describe('Instructions bileşeni', () => {
  test('header ve text props ile render eder', () => {
    render(<Instructions header="Başlık" text="Açıklama metni" />)
    expect(screen.getByText(/Başlık:/)).toBeInTheDocument()
    expect(screen.getByText('Açıklama metni')).toBeInTheDocument()
  })

  test('header verilmeyince sadece text gösterilir', () => {
    render(<Instructions text="Sadece metin var" />)
    expect(screen.queryByText(/:/)).not.toBeInTheDocument() // Başlık yok
    expect(screen.getByText('Sadece metin var')).toBeInTheDocument()
  })

  test('hidden true ise hiçbir içerik render edilmez', () => {
    const { container } = render(<Instructions header="Başlık" text="Metin" hidden={true} />)
    expect(container).toBeEmptyDOMElement()
  })

  test('hidden false ise içerik görünür', () => {
    render(<Instructions header="Başlık" text="Metin" hidden={false} />)
    expect(screen.getByText(/Başlık:/)).toBeInTheDocument()
    expect(screen.getByText('Metin')).toBeInTheDocument()
  })
})