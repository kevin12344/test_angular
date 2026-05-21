import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent implements OnInit {
  serverMessage: string = '載入中...';

  constructor(private http: HttpClient, private router: Router, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.serverMessage = '連線中...';
    this.http.get<any>('/api/login/api/me')
      .subscribe({
        next: (res) => { this.serverMessage = `${res.employee_id} ${res.employee_name}`; this.cdr.detectChanges(); },
        error: (err) => { this.serverMessage = `錯誤 ${err.status}：${err.error?.message || '無法連線'}`; this.cdr.detectChanges(); }
      });
  }

  // 3. 定義登出方法
  logout() {
    localStorage.removeItem('auth_token'); // 清除 Token
    this.router.navigate(['/login']);      // 跳回登入頁面
  }
}