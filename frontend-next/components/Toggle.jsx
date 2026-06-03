"use client";

import { useState } from "react";
import styles from "./Toggle.module.css";

// 외부 라이브러리 없이 직접 만든 ON/OFF 스위치.
// - 비제어: <Toggle defaultOn /> 처럼 내부 state 로 동작
// - 제어:   <Toggle on={value} onChange={fn} /> 처럼 부모가 값을 소유 (설정 저장용)
export default function Toggle({ defaultOn = false, on, onChange, disabled = false }) {
  const isControlled = on !== undefined;
  const [internalOn, setInternalOn] = useState(defaultOn);
  const value = isControlled ? on : internalOn;

  function handle() {
    const next = !value;
    if (!isControlled) setInternalOn(next);
    onChange?.(next);
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={value}
      disabled={disabled}
      className={`${styles.track} ${value ? styles.on : ""}`}
      onClick={handle}
    >
      <span className={styles.thumb} />
    </button>
  );
}
