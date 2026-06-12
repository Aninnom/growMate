"use client";

import { useState, useEffect } from "react";
import { getProfileApi, saveProfileApi } from "@/lib/api";

export const DEFAULT_PROFILE = {
  name: "그로우메이트",
  species: "몬스테라",
  avatar: "happy",
  adoptionDate: "",
  preferences: {
    tempMin: 18,
    tempMax: 28,
    humidityMin: 60,
    humidityMax: 80,
    soilMoistureMin: 40,
    soilMoistureMax: 70,
    wateringCycle: 7,
    lightLevel: "보통",
  },
};

const STORAGE_KEY = "growmate_profile";

export function useProfile() {
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      // 1순위: 백엔드 저장 프로필(앱·LCD 공통 기준). 실패/미연동 시 localStorage → 기본값.
      try {
        const remote = await getProfileApi();
        if (remote && remote.preferences) {
          if (alive) setProfile(remote);
          try { localStorage.setItem(STORAGE_KEY, JSON.stringify(remote)); } catch {}
          if (alive) setLoaded(true);
          return;
        }
      } catch {
        // 백엔드 미연동/오류 → localStorage 로 폴백
      }
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw && alive) setProfile(JSON.parse(raw));
      } catch {
        // ignore parse errors
      }
      if (alive) setLoaded(true);
    })();
    return () => { alive = false; };
  }, []);

  function saveProfile(next) {
    setProfile(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore storage errors
    }
    // 백엔드에도 저장 → 같은 적정 범위로 LCD 표정 판단
    saveProfileApi(next).catch(() => {});
  }

  return { profile, saveProfile, loaded };
}
