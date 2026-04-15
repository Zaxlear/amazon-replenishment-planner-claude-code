import React from 'react';
import { DatePicker, Button, Space } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import { disableNonSaturday, nextSaturday } from '../../utils/dateUtils';

interface Props {
  value?: string | null;
  onChange?: (date: string) => void;
  minDate?: string;
  maxDate?: string;
}

const SaturdayDatePicker: React.FC<Props> = ({ value, onChange, minDate, maxDate }) => {
  const handleChange = (date: Dayjs | null) => {
    if (date && onChange) {
      onChange(date.format('YYYY-MM-DD'));
    }
  };

  const disabledDate = (current: Dayjs): boolean => {
    if (disableNonSaturday(current)) return true;
    if (minDate && current.isBefore(dayjs(minDate), 'day')) return true;
    if (maxDate && current.isAfter(dayjs(maxDate), 'day')) return true;
    return false;
  };

  const now = dayjs();
  const thisSat = nextSaturday(now);
  const nextSat = thisSat.add(7, 'day');
  const twoWeeks = thisSat.add(14, 'day');

  return (
    <Space direction="vertical" size="small">
      <DatePicker
        value={value ? dayjs(value) : null}
        onChange={handleChange}
        disabledDate={disabledDate}
        format="YYYY-MM-DD (ddd)"
        placeholder="选择周六发货日期"
        style={{ width: '100%' }}
      />
      <Space size="small">
        <Button size="small" onClick={() => onChange?.(thisSat.format('YYYY-MM-DD'))}>
          本周六
        </Button>
        <Button size="small" onClick={() => onChange?.(nextSat.format('YYYY-MM-DD'))}>
          下周六
        </Button>
        <Button size="small" onClick={() => onChange?.(twoWeeks.format('YYYY-MM-DD'))}>
          两周后
        </Button>
      </Space>
    </Space>
  );
};

export default SaturdayDatePicker;
