export function formatNumber(n: number): string {
  return n.toLocaleString('zh-CN');
}

export function formatUnitLabel(shipDate: string, region: string): string {
  const d = new Date(shipDate);
  const regionMap: Record<string, string> = {
    west: '美西',
    central: '美中',
    east: '美东',
  };
  return `${d.getMonth() + 1}月${d.getDate()}日-${regionMap[region] || region}`;
}
