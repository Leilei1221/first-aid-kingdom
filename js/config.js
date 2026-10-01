/* Supabase 連線設定（教室管理系統專案）。
 * anonKey 是「可公開」的金鑰，設計上就會出現在前端；資料安全靠資料表的 RLS，不靠金鑰保密。
 * 絕對不要在這裡放 service_role 金鑰。 */
window.FA_CONFIG={
  url:'https://fcstpyiggvhduaztwlrf.supabase.co',
  anonKey:'sb_publishable_6Xo2ujpvxUS3fblNYpw7iA_2No_Ja34'
};
