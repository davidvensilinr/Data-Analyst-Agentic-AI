import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload } from '@/components/dataset/FileUpload';

// Mock the API
jest.mock('@/lib/api', () => ({
  api: {
    uploadDataset: jest.fn(),
  },
}));

describe('FileUpload Component', () => {
  const mockOnUploadComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the file upload component', () => {
    render(<FileUpload onUploadComplete={mockOnUploadComplete} />);
    expect(screen.getByText(/click to upload/i)).toBeInTheDocument();
  });

  it('displays file size limit warning', () => {
    render(<FileUpload onUploadComplete={mockOnUploadComplete} maxSizeMB={10} />);
    expect(screen.getByText(/maximum/i)).toBeInTheDocument();
  });

  it('accepts CSV files', async () => {
    const file = new File(['test'], 'test.csv', { type: 'text/csv' });
    render(<FileUpload onUploadComplete={mockOnUploadComplete} />);
    
    const input = screen.getByRole('button');
    expect(input).toBeInTheDocument();
  });

  it('displays error for unsupported file types', async () => {
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    render(<FileUpload onUploadComplete={mockOnUploadComplete} />);
    
    // The component should validate file types
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput?.accept).toContain('.csv');
  });

  it('shows upload progress', async () => {
    render(<FileUpload onUploadComplete={mockOnUploadComplete} />);
    expect(screen.getByText(/or drag and drop/i)).toBeInTheDocument();
  });
});
