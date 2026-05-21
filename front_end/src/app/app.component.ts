import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true, // 確保這行存在
  imports: [RouterOutlet], // 必須匯入 RouterOutlet 才能在 HTML 用 <router-outlet>
  templateUrl: './app.component.html', // 建議檢查檔名是否一致
  styleUrl: './app.component.css'    // 建議檢查檔名是否一致
})
export class AppComponent { // 建議用預設名稱 AppComponent
  title = signal('my-first-app');
}