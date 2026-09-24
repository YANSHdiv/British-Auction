import {
  AuthResponse,
  User,
  RFQ,
  Bid,
  AuctionRankingResponse,
  SupplierRankingItem,
  ActivityLog,
  CreateRFQPayload,
  CreateBidPayload,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
    } catch {
      // Keep default error message
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse<AuthResponse>(res);
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<User>(res);
  },

  // RFQs
  async listRfqs(status?: string): Promise<RFQ[]> {
    const query = status && status !== 'ALL' ? `?status=${status}` : '';
    const res = await fetch(`${API_BASE_URL}/rfqs${query}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<RFQ[]>(res);
  },

  async getRfq(id: string): Promise<RFQ> {
    const res = await fetch(`${API_BASE_URL}/rfqs/${id}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<RFQ>(res);
  },

  async createRfq(payload: CreateRFQPayload): Promise<RFQ> {
    const res = await fetch(`${API_BASE_URL}/rfqs`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<RFQ>(res);
  },

  // Auctions & Bids
  async getAuctionRankings(rfqId: string): Promise<AuctionRankingResponse> {
    const res = await fetch(`${API_BASE_URL}/auctions/${rfqId}/ranking`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<AuctionRankingResponse>(res);
  },

  async getAuctionBids(rfqId: string): Promise<Bid[]> {
    const res = await fetch(`${API_BASE_URL}/auctions/${rfqId}/bids`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<Bid[]>(res);
  },

  async getAuctionActivity(rfqId: string): Promise<ActivityLog[]> {
    const res = await fetch(`${API_BASE_URL}/auctions/${rfqId}/activity`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<ActivityLog[]>(res);
  },

  async getMyBid(rfqId: string): Promise<SupplierRankingItem | null> {
    const res = await fetch(`${API_BASE_URL}/auctions/${rfqId}/my-bid`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<SupplierRankingItem | null>(res);
  },

  async submitBid(rfqId: string, payload: CreateBidPayload): Promise<Bid> {
    const res = await fetch(`${API_BASE_URL}/auctions/${rfqId}/bids`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<Bid>(res);
  },
};
