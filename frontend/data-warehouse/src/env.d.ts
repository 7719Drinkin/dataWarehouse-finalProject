interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
    // 你可以在这里添加更多 VITE_ 开头的环境变量
}
  
interface ImportMeta {
    readonly env: ImportMetaEnv;
}
  