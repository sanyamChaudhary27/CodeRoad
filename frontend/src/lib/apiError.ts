import axios from 'axios';

interface ValidationIssue {
  msg?: string;
}

interface ApiErrorPayload {
  detail?: string | ValidationIssue[];
}

export interface ApiErrorInfo {
  code?: string;
  status?: number;
  detail?: string | ValidationIssue[];
  hasResponse: boolean;
}

export const getApiErrorInfo = (error: unknown): ApiErrorInfo => {
  if (!axios.isAxiosError<ApiErrorPayload>(error)) {
    return { hasResponse: false };
  }
  return {
    code: error.code,
    status: error.response?.status,
    detail: error.response?.data?.detail,
    hasResponse: Boolean(error.response),
  };
};

export const getApiErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof Error && !axios.isAxiosError(error)) return error.message || fallback;
  const info = getApiErrorInfo(error);
  if (typeof info.detail === 'string') return info.detail;
  if (Array.isArray(info.detail) && info.detail[0]?.msg) return info.detail[0].msg;
  return fallback;
};
