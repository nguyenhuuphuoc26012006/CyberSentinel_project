export type SecurityEvent = {
  id: number;
  source: string;
  event_type: string;
  source_ip: string | null;
  username: string | null;
  severity: string;
  message: string | null;
  created_at: string;
};

export type Alert = {
  id: number;
  title: string;
  rule_id: string;
  severity: string;
  source_ip: string | null;
  description: string;
  status: string;
  created_at: string;
};
