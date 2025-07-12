function convert2cartesian(rx, ry, theta) {
    const x = rx * Math.cos(theta);
    const y = ry * Math.sin(theta);
    return {x:x,y:y};
}

function saveData(data){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'write_data.php'); 
    xhr.setRequestHeader('Content-Type', 'application/json');
    // console.log(JSON.stringify({filedata: data}))
    xhr.send(JSON.stringify({filedata: data}));
  }