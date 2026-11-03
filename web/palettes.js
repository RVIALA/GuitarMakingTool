export const palettes={
  rainbow:[[110,0,160],[0,0,255],[0,190,255],[0,200,70],[255,240,0],[255,120,0],[230,0,0]],
  balance:[[35,73,146],[93,154,204],[245,245,235],[226,126,77],[153,30,48]],
  viridis:[[68,1,84],[59,82,139],[33,145,140],[94,201,98],[253,231,37]],
  magma:[[0,0,4],[59,15,112],[140,41,129],[221,73,104],[254,159,109],[252,253,191]],
  turbo:[[48,18,59],[55,94,214],[36,170,224],[70,224,120],[189,235,45],[249,174,38],[224,65,15],[122,4,3]],
  gray:[[10,16,23],[247,248,240]]
};
export function paletteRGB(name,t){
  const a=palettes[name]||palettes.viridis,u=Math.max(0,Math.min(1,t))*(a.length-1),i=Math.min(a.length-2,Math.floor(u)),s=u-i;
  return a[i].map((v,k)=>v*(1-s)+a[i+1][k]*s);
}
export function drawPalette(canvas,name,labels=['0','1']){
  const w=canvas.width=360,h=canvas.height=42,g=canvas.getContext('2d');g.clearRect(0,0,w,h);
  for(let x=0;x<w;x++){g.fillStyle=`rgb(${paletteRGB(name,x/(w-1)).join(',')})`;g.fillRect(x,0,1,17);}
  g.fillStyle='#536c69';g.font='11px system-ui';g.textAlign='left';g.fillText(labels[0],0,34);g.textAlign='right';g.fillText(labels[1],w,34);
}
