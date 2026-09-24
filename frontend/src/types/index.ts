export type UserRole = 'BUYER' | 'SUPPLIER';

export type RFQStatus = 'DRAFT' | 'SCHEDULED' | 'ACTIVE' | 'CLOSED' | 'FORCE_CLOSED';

export type ExtensionTriggerType = 'BID_RECEIVED' | 'ANY_RANK_CHANGE' | 'L1_RANK_CHANGE';

export type ActivityEventType =
  | 'RFQ_CREATED'
  | 'BID_SUBMITTED'
  | 'AUCTION_EXTENDED'
  | 'AUCTION_CLOSED'
  | 'AUCTION_FORCE_CLOSED';

export interface User {
  id: string;
  email: string;
  full_name: string;
  company_name: string;
  role: UserRole;
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuctionConfiguration {
  id: string;
  rfq_id: string;
  british_auction_enabled: boolean;
  trigger_window_minutes: number;
  extension_duration_minutes: number;
  extension_trigger_type: ExtensionTriggerType;
  current_close_time: string;
  extension_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface RFQ {
  id: string;
  name: string;
  reference_id: string;
  pickup_service_date: string;
  status: RFQStatus;
  effective_status: RFQStatus;
  buyer_id: string;
  bid_start_time: string;
  bid_close_time: string;
  forced_bid_close_time: string;
  current_close_time: string;
  lowest_bid_amount: string | number | null;
  bid_count: number;
  supplier_count: number;
  auction_config?: AuctionConfiguration;
  created_at: string;
  updated_at: string;
}

export interface Bid {
  id: string;
  rfq_id: string;
  supplier_id: string;
  carrier_name: string;
  freight_charges: string | number;
  origin_charges: string | number;
  destination_charges: string | number;
  total_amount: string | number;
  transit_time_days: number;
  validity_date: string;
  created_at: string;
  rank_label?: string | null;
  supplier?: User;
}

export interface SupplierRankingItem {
  rank: number;
  rank_label: string;
  supplier_id: string;
  supplier_name: string;
  company_name: string;
  best_bid_id: string;
  total_amount: string | number;
  freight_charges: string | number;
  origin_charges: string | number;
  destination_charges: string | number;
  transit_time_days: number;
  validity_date: string;
  submitted_at: string;
  bid_count: number;
}

export interface AuctionRankingResponse {
  rfq_id: string;
  rankings: SupplierRankingItem[];
  lowest_bid_amount: string | number | null;
  l1_supplier_id: string | null;
}

export interface ActivityLog {
  id: string;
  rfq_id: string;
  event_type: ActivityEventType;
  supplier_id?: string | null;
  supplier_name?: string | null;
  bid_id?: string | null;
  old_close_time?: string | null;
  new_close_time?: string | null;
  extension_reason?: string | null;
  metadata_json?: Record<string, any> | null;
  created_at: string;
}

export interface CreateRFQPayload {
  name: string;
  reference_id: string;
  pickup_service_date: string;
  bid_start_time: string;
  bid_close_time: string;
  forced_bid_close_time: string;
  auction_config?: {
    british_auction_enabled: boolean;
    trigger_window_minutes: number;
    extension_duration_minutes: number;
    extension_trigger_type: ExtensionTriggerType;
  };
}

export interface CreateBidPayload {
  carrier_name: string;
  freight_charges: number | string;
  origin_charges: number | string;
  destination_charges: number | string;
  transit_time_days: number;
  validity_date: string;
}
