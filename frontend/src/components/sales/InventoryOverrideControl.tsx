import React, { useState } from 'react';
import { Modal, InputNumber, Input, message } from 'antd';

interface Props {
  open: boolean;
  date: string;
  currentValue: number;
  onCancel: () => void;
  onConfirm: (value: number, reason: string) => void;
}

const InventoryOverrideControl: React.FC<Props> = ({
  open, date, currentValue, onCancel, onConfirm,
}) => {
  const [value, setValue] = useState(currentValue);
  const [reason, setReason] = useState('');

  const handleOk = () => {
    if (value < 0) {
      message.error('校正值不能为负数');
      return;
    }
    onConfirm(value, reason);
    setReason('');
  };

  return (
    <Modal
      title="校正期初库存"
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      okText="确认校正"
      cancelText="取消"
    >
      <div style={{ marginBottom: 12 }}>
        <strong>日期:</strong> {date}
      </div>
      <div style={{ marginBottom: 12 }}>
        <strong>原计算值:</strong> {currentValue}
      </div>
      <div style={{ marginBottom: 12 }}>
        <div>校正为:</div>
        <InputNumber
          value={value}
          onChange={(v) => setValue(v || 0)}
          min={0}
          style={{ width: '100%' }}
        />
      </div>
      <div style={{ marginBottom: 12 }}>
        <div>原因 (选填):</div>
        <Input.TextArea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={2}
          placeholder="例: 实际盘点差异"
        />
      </div>
      <div style={{ color: '#faad14' }}>
        校正后将影响 {date} 之后所有日期的库存计算。
      </div>
    </Modal>
  );
};

export default InventoryOverrideControl;
