import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';

// 1. 防止「未登入」的人進入「主畫面」 (一般的 Auth Guard)
export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const token = localStorage.getItem('auth_token');

  if (token) {
    return true; // 有 Token，准許通過
  } else {
    router.navigate(['/login']); // 沒 Token，踢回登入頁
    return false;
  }
};

// 2. 防止「已登入」的人進入「登入頁」 (這就是你現在要的功能)
export const loginGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const token = localStorage.getItem('auth_token');

  if (token) {
    router.navigate(['/main']); // 已經有 Token 了，直接去主畫面
    return false; // 不准進入登入頁
  } else {
    return true; // 沒 Token，准許進入登入頁
  }
};