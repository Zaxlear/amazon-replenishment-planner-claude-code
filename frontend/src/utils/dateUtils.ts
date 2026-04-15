import dayjs, { Dayjs } from 'dayjs';

export function isSaturday(date: Dayjs): boolean {
  return date.day() === 6;
}

export function nextSaturday(from: Dayjs = dayjs()): Dayjs {
  const day = from.day();
  const daysUntilSat = day <= 6 ? (6 - day) || 7 : 6;
  return from.add(daysUntilSat, 'day');
}

export function disableNonSaturday(current: Dayjs): boolean {
  return current.day() !== 6;
}

export function formatDate(date: string): string {
  return dayjs(date).format('YYYY-MM-DD');
}

export function formatDateCN(date: string): string {
  const d = dayjs(date);
  return `${d.month() + 1}月${d.date()}日`;
}

const REGION_MAP: Record<string, string> = {
  west: '美西',
  central: '美中',
  east: '美东',
};

export function regionLabel(region: string): string {
  return REGION_MAP[region] || region;
}
