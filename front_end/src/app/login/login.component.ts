import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent {
    loginData = { username: '', password: '' };

    constructor(private http: HttpClient, private router: Router) {}

    private async sha256Hex(text: string): Promise<string> {
        const buf = new TextEncoder().encode(text);
        const hash = await crypto.subtle.digest('SHA-256', buf);
        return Array.from(new Uint8Array(hash))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // 登入
    async onSubmit() {
        const passwordHash = await this.sha256Hex(this.loginData.password);
        const payload = { username: this.loginData.username, password: passwordHash };

        this.http.post<any>('/api/login/api/test', payload)
            .subscribe({
            next: (res) => {
                if (res.success && res.token) {
                    localStorage.setItem('auth_token', res.token);
                    this.router.navigate(['/main']);
                } else {
                    alert('登入失敗：' + (res.message || '帳號或密碼錯誤'));
                }
            },
            error: (err) => {
                console.error('登入請求發生錯誤:', err);
                alert('伺服器連線失敗');
            }
        });
    }

    // 清除按鈕的方法
    onClear() {
        this.loginData = { username: '', password: '' };
    }
}
