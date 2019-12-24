function validatecallcentre(){
    a=document.getElementById(inputfname).value;
    $(document).ready(function(){
        $('#button').click(function(){
        var user=$('#inputfname').val();
        if(user==""){
            $('#show_error').html('**The username must be filled.');
            $('#show_error').css('color','red');
            return false;
            }
        });
    });
    b=document.getElementById(inputlname).value;
    c=document.getElementById(inputproduct).value;
    d=document.getElementById(inputfault).value;
    e=document.getElementById(inputaddress).value;
    f=document.getElementById(inputcity).value;
    g=document.getElementById(inputmobile).value;
    h=document.getElementById(inputpin).value;
    console.log(a+b+c+d+e+f+g+h).value;
    alert('Ok');
    
}
console.log('working fine');
