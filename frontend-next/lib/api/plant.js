// 식물 상태 / 프로필 API — docs/api.md §1.1, §4.3
import { apiFetch, USE_MOCK, mockDelay } from "./client";
import { plant } from "@/lib/data/plant";
import { profile } from "@/lib/data/settings";

// GET /plant/status — 홈 캐릭터 표정 + 상태 카드
export function getPlantStatus() {
  if (USE_MOCK) {
    return mockDelay({
      mood: plant.mood, // happy | thirsty | sleepy
      statusTitle: plant.statusTitle,
      statusDesc: plant.statusDesc,
      updatedAt: new Date().toISOString(),
    });
  }
  return apiFetch("/plant/status");
  // 표시용 "방금 전" 변환은 화면에서 updatedAt(ISO)로 처리
}

// GET /plant/profile — 설정 프로필 카드
export function getPlantProfile() {
  if (USE_MOCK) {
    return mockDelay({ name: profile.name, species: "몬스테라", connection: "ok" });
  }
  return apiFetch("/plant/profile");
}

// GET /profile — 식물 프로필(이름·종·적정 환경 범위 preferences).
// 적정 범위는 센서 상태/LCD 표정 판단의 단일 기준이 된다.
// mock 모드(백엔드 미연동)에서는 null 을 반환해 훅이 localStorage 로 동작하게 한다.
export function getProfileApi() {
  if (USE_MOCK) return mockDelay(null);
  return apiFetch("/profile");
}

// PUT /profile — 프로필 전체 저장(덮어쓰기).
export function saveProfileApi(next) {
  if (USE_MOCK) return mockDelay(next);
  return apiFetch("/profile", { method: "PUT", body: next });
}
