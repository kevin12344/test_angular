import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // 必須導入這個才能用 ngModel
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule], // 確保這裡有 FormsModule
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent {
    loginData = { username: '', password: '' };

    constructor(private http: HttpClient, private router: Router) {}
    
    // 登入
    onSubmit() {
        console.log('正在嘗試登入...', this.loginData);

        // 第一步：發送登入請求
        this.http.post<any>('/api/login/api/test', this.loginData)
            .subscribe({
            next: (res) => {
                console.log('登入 API 回傳結果:', res);

                if (res.success && res.token) {
                localStorage.setItem('auth_token', res.token);
                this.router.navigate(['/main']);
                } else {
                console.warn('登入失敗，後端回傳 success 為 false 或沒給 token');
                alert('登入失敗：' + (res.message || '帳號或密碼錯誤'));
                }
            },
            error: (err) => {
                console.error('登入請求本身發生錯誤 (500 或網路問題):', err);
                alert('伺服器連線失敗');
            }
        });
    }

    // 清除按鈕的方法
    onClear() {
        this.loginData = { username: '', password: '' };
    }
}