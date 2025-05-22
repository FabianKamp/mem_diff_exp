function convert2cartesian(radius, theta) {
    const x = radius * Math.cos(theta);
    const y = radius * Math.sin(theta);
    return {x:x,y:y};
}

function saveData(data){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'write_data.php'); 
    xhr.setRequestHeader('Content-Type', 'application/json');
    // console.log(JSON.stringify({filedata: data}))
    xhr.send(JSON.stringify({filedata: data}));
  }