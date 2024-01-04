const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/backend',  // Ruta correspondiente a tus archivos PHP
    createProxyMiddleware({
      target: 'http://localhost',  // Cambia esto según tu configuración de XAMPP
      changeOrigin: true,
    })
  );
};
