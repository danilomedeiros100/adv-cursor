// Script para verificar o token no localStorage
console.log('=== VERIFICAÇÃO DO TOKEN ===');

// Verificar se estamos no navegador
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('access_token');
  
  if (token) {
    console.log('✅ Token encontrado no localStorage');
    console.log('Token:', token.substring(0, 50) + '...');
    
    // Decodificar o token JWT (parte do payload)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      console.log('Payload do token:', payload);
      
      // Verificar se o token expirou
      const now = Math.floor(Date.now() / 1000);
      const exp = payload.exp;
      
      if (exp && exp < now) {
        console.log('❌ Token expirado!');
        console.log('Expira em:', new Date(exp * 1000));
        console.log('Agora:', new Date(now * 1000));
      } else {
        console.log('✅ Token válido');
        console.log('Expira em:', new Date(exp * 1000));
      }
    } catch (error) {
      console.log('❌ Erro ao decodificar token:', error);
    }
  } else {
    console.log('❌ Nenhum token encontrado no localStorage');
  }
  
  // Verificar outros dados de autenticação
  const user = localStorage.getItem('auth-storage');
  if (user) {
    console.log('Dados de autenticação:', JSON.parse(user));
  }
} else {
  console.log('❌ Este script deve ser executado no navegador');
}
