function show_ig(tag) {
    if(navigator.appName == 'Microsoft Internet Explorer') {
	    el = document.getElementById(tag).style.display
        var agree=confirm("CSS display property does nor work correctly on Internet Explorer. Please try a true web browser.");
        /* document.getElementById(tag).style.display = inline; */
        /* document.getElementById(tag).style.zoom = 1; */
    }
    else{
        if (document.getElementById(tag).style.display == "block"){
            document.getElementById(tag).style.display = "none";
        }
        else{
            document.getElementById(tag).style.display = "block";
        }
    }

}
function display_action_comment (menu,arrow)
{
    /* l'element possede t'il un identifiant ? */
    if (document.getElementById)
    {
        /* oui, lecture de l'element */
        thisMenu = document.getElementById(menu)
        /* est-il visible ? */
        if (thisMenu.style.display == "block")
        {
            /* on remet la fleche vers le bas */
            arrow.style.background='url(img/down_arrow_2.png) no-repeat'
            /* oui, on le cache */
            /* thisMenu.style.display = "none" */
        }
        else
        {
            /* on met la fleche vers le haut */
            arrow.style.background='url(img/up_arrow_2.png) no-repeat'
            /* non, on l'affiche */
            /* thisMenu.style.display = "block" */
        }
        return false
    }
    else
    {
        /* non, pas d'identifiant */
        return true
    }
}
/*
 * NCleanGrey_standard.js
 */
function cms_page_tab_style() {
	linksExternal(); 
	defaultFocus();
 	if (document.getElementById('navt_tabs')) {
		var el = document.getElementById('navt_tabs');
		_add_show_handlers(el);
	}
 	if (document.getElementById('page_tabs')) {
		var el = document.getElementById('page_tabs');
		_add_show_handlers(el);
	}
}

function IEhover() {
		if (document.getElementById('nav')) {
			cssHover('nav','LI');	
		}
	 	if (document.getElementById('navt_tabs')) {
			cssHover('navt_tabs','DIV');
		}
	 	if (document.getElementById('page_tabs')) {
			cssHover('page_tabs','DIV');
		}
}

function cssHover(tagid,tagname) {
	var sfEls = document.getElementById(tagid).getElementsByTagName(tagname);
	for (var i=0; i<sfEls.length; i++) {
		sfEls[i].onmouseover=function() {
			this.className+=" cssHover";
		}
		sfEls[i].onmouseout=function() {
			this.className=this.className.replace(new RegExp(" cssHover\\b"), "");
		}
	}
}

function change(id, newClass, oldClass) {
	identity=document.getElementById(id);
	if (identity.className == oldClass) {
		identity.className=newClass;
	} else {
		identity.className=oldClass;
	}
}

function _add_show_handlers(navbar) {
    var tabs = navbar.getElementsByTagName('div');
    for (var i = 0; i < tabs.length; i += 1) {
	tabs[i].onmousedown = function() {
	    for (var j = 0; j < tabs.length; j += 1) {
			tabs[j].className = '';
			document.getElementById(tabs[j].id + "_c").style.display = 'none';
	    }
	    this.className = 'active';
	    document.getElementById(this.id + "_c").style.display = 'block';
	    return true;
	};
    }
    var activefound=0;
    for (var i = 0; i < tabs.length; i += 1) {
    	if (tabs[i].className=='active') activefound=i;
    }
    tabs[activefound].onmousedown();
}

function activatetab(index) {
	var el=0;
	if (document.getElementById('navt_tabs')) {
		el = document.getElementById('navt_tabs');
		
	} else {
 	  if (document.getElementById('page_tabs')) {
		  el = document.getElementById('page_tabs');
	  }
	}
	if (el==0) return;
	var tabs = navbar.getElementsByTagName('div');
	tabs[index].onmousedown();
}

function linksExternal()	{
	if (document.getElementsByTagName)	{
		var anchors = document.getElementsByTagName("a");
		for (var i=0; i<anchors.length; i++)	{
			var anchor = anchors[i];
			if (anchor.getAttribute("rel") == "external")	{
				anchor.target = "_blank";
			}
		}
	}
}

//use <input class="defaultfocus" ...>
function defaultFocus() {

   if (!document.getElementsByTagName) {
        return;
   }

   var anchors = document.getElementsByTagName("input");
   for (var i=0; i<anchors.length; i++) {
      var anchor = anchors[i];
      var classvalue;

      //IE is broken! 
      if(navigator.appName == 'Microsoft Internet Explorer') {
            classvalue = anchor.getAttribute('className');
      } else {
            classvalue = anchor.getAttribute('class');
      }

      if (classvalue!=null) {
                var defaultfocuslocation = classvalue.indexOf("defaultfocus");
                if (defaultfocuslocation != -1) {
                	anchor.focus();
			var defaultfocusselect = classvalue.indexOf("selectall");
			if (defaultfocusselect != -1) {
				anchor.select();
			}
                }
        }
   }
}

function togglecollapse(cid)
{
  document.getElementById(cid).style.display=(document.getElementById(cid).style.display!="block")? "block" : "none";
}
function setnormeactivetab()
{
	var navbar = document.getElementById('page_tabs');
	var tabs = navbar.getElementsByTagName('div');
	for (var j = 0; j < tabs.length; j += 1) {
		tabs[j].className = '';
		document.getElementById(tabs[j].id + "_c").style.display = 'none';
	}
	/* Make norme active */
	tabs[5].className = 'active';
	document.getElementById("normes_c").style.display = 'block';
	return true;
}