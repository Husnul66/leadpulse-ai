const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Lead {
  id: number;
  company_name: string;
  company_url: string;
  target_audience?: string;
  status: string;
  created_at: string;
}

export interface LeadCreatePayload {
  company_name: string;
  company_url: string;
  target_audience?: string;
}

export interface MessageGeneratePayload {
  outreach_channel?: "cold_email" | "linkedin" | "twitter_dm";
  sender_name?: string;
  sender_company?: string;
  value_proposition?: string;
  additional_instructions?: string;
}

export interface GeneratedMessage {
  id: number;
  lead_id: number;
  outreach_channel: string;
  generated_content: string;
  created_at: string;
}

// Fetch all leads
export async function fetchLeads(): Promise<Lead[]> {
  const res = await fetch(`${API_BASE_URL}/leads/`);
  if (!res.ok) throw new Error("Failed to fetch leads");
  return res.json();
}

// Create a new lead
export async function createLead(payload: LeadCreatePayload): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/leads/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create lead");
  return res.json();
}

// Trigger AI Message Generation for a lead
export async function generateMessage(leadId: number, payload: MessageGeneratePayload = {}): Promise<GeneratedMessage> {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate AI message");
  }
  return res.json();
}

// Fetch generated messages for a specific lead
export async function fetchLeadMessages(leadId: number): Promise<GeneratedMessage[]> {
  const res = await fetch(`${API_BASE_URL}/leads/${leadId}/messages`);
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}