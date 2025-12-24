/*! 
 * include.js - v1.2.0
 * Copyright (c) 2022 StichtingWebsite
 * https://stichtingwebsite.org/
 */

function include(file) {
  var script = document.createElement('script');
  script.src = file;
  script.type = 'text/javascript';
  script.defer = true;
  document.getElementsByTagName('head')[0].appendChild(script);
}
