import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import Name from '../pages/recordDatabase/components/Name';
import PopUp from '../pages/recordDatabase/components/PopUp';
import DatabaseControlButtons from '../pages/recordDatabase/components/DatabaseControlButtons';

// useNavigate hook'unu mock'la
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

// global.fetch ve global.WebSocket'i mock'la
global.fetch = vi.fn();


// Testler

describe('RecordDatabase Bileşenleri ve Sayfası Testleri', () => {

  // Her testten önce mock'ları ve timer'ları temizle
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    fetch.mockResolvedValue({ ok: true }); // fetch için varsayılan başarılı yanıt
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // Alt Bileşen Testleri

  describe('Name Component', () => {
    it('input değeri değiştiğinde state güncellenmeli', () => {
      render(<Name checkName={() => {}} hidden={false} />);
      const input = screen.getByPlaceholderText('Bir isim giriniz');
      fireEvent.change(input, { target: { value: 'Ayşe' } });
      expect(input.value).toBe('Ayşe');
    });

    it('isim girilip butona basıldığında checkName fonksiyonu çağrılmalı', () => {
      const checkNameMock = vi.fn();
      render(<Name checkName={checkNameMock} hidden={false} />);
      const input = screen.getByPlaceholderText('Bir isim giriniz');
      const button = screen.getByText('Gönder');

      fireEvent.change(input, { target: { value: 'Fatma' } });
      fireEvent.click(button);

      expect(checkNameMock).toHaveBeenCalledWith('Fatma');
    });
  });

  describe('DatabaseControlButtons Component', () => {
    it('başlangıçta "Başla" butonu görünmeli', () => {
      render(<DatabaseControlButtons onStart={() => {}} onStop={() => {}} hidden={false} />);
      expect(screen.getByRole('button', { name: 'Başla' })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: 'Durdur' })).not.toBeInTheDocument();
    });

    it('"Başla" butonuna tıklanınca onStart çağrılmalı ve "Durdur" butonu görünmeli', () => {
      const onStartMock = vi.fn();
      render(<DatabaseControlButtons onStart={onStartMock} onStop={() => {}} hidden={false} />);
      fireEvent.click(screen.getByRole('button', { name: 'Başla' }));

      expect(onStartMock).toHaveBeenCalledTimes(1);
      expect(screen.getByRole('button', { name: 'Durdur' })).toBeInTheDocument();
    });
  });

  describe('PopUp Component', () => {
    it('hidden true ise bir şey render etmemeli', () => {
      const { container } = render(<PopUp text="Test" hidden={true} color="red" />);
      expect(container.firstChild).toBeNull();
    });

    it('hidden false ise doğru metin ile mesajı göstermeli', () => {
      render(<PopUp text="Başarılı!" hidden={false} color="green" />);
      const label = screen.getByText('Başarılı!');
      expect(label).toBeInTheDocument();
    });
  });
});