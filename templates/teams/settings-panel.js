
var ACTIVE_CLASS  =- "current";
var PAINEL_MARKER = "painel-";

var MENU_SELECTOR = ".sub-settings-panel";
var CONTAINER_SELECTOR = ".painel-holder";
var TEAM_SLUG = "{{team.slug}}";
var ON_PROJECT_SAVED = "onProjectSaved";

var AsyncPainel = Class.$extend({
    load: function (url){
        var oldEl = $(this.el).children().remove();
        $(this.el).innerHTML(icanhaz.IMAGE_PRELOADER);
        $.ajax(url, {
            success: function(res){
                $(this.el).innerHTML(oldEl)
                this.onLoadDone(res);
            }
        });
    }
});

var ProjectModel = Class.$extend({
    __init__: function(data){
        this.name = data.name;
        this.slug = data.slug;
        this.description = data.description;
        this.pk = data.pk;
        this.teamSlug = TEAM_SLUG;
    }
});

var ProjectEditPanel = Class.$extend({
     __init__: function(pModel){
         this.model = pModel;
         this.el = ich.projectEditPanel(pModel);
         this.onSaveClicked = _.bind(this.onSaveClicked, this);
         this.onDeleteClicked = _.bind(this.onDeleteClicked, this);
         this.onChangeProjectReturned = _.bind(this.onChangeProjectReturned, this);
         $(".project-delete", this.el).click(this.onDeleteClicked);
         $(".project-save", this.el).click(this.onSaveClicked);
         
    },
    getValuesFromForm: function(form){
        var inputs = $(':input', form);

        var values = {};
        inputs.each(function() {
            values[this.name] = $(this).val() || null;
        });
        return values;

    },
    onSaveClicked: function(e){
        e.preventDefault();
        var values = this.getValuesFromForm($("form", this.el));
        TeamsApiV2.project_edit(
            TEAM_SLUG,
            values.pk,
            values.name,
            values.slug,
            values.description,
            values.order ,
            this.onChangeProjectReturned
        )
        return false;
    },
    onChangeProjectReturned: function(data){
        var res = data;
        if (res && res.success){
            $.jGrowl(res.msg);
            if (res.obj){
                var model = new ProjectModel(res.obj);
                this.el.trigger(ON_PROJECT_SAVED, model);
                
            }
            // show errors
        }else{
            $.jGrowl.error(data.result.message);
            if(data.result && data.result.errors){

            }
        }
    },
    onDeleteClicked: function(e){
        e.preventDefault();
        
        return false;
    }
    
});

var ProjectSelectionButton = Class.$extend({
    __init__: function(pModel){
        this.model = pModel;

    }
});

var ProjectPainel  = AsyncPainel.$extend({
    __init__: function(){
        this.onProjectListLoaded = _.bind(this.onProjectListLoaded, this);
        this.onNewProjectClicked = _.bind(this.onNewProjectClicked, this);
        this.onProjectSaved = _.bind(this.onProjectSaved, this);
        this.el = ich.projectPanel();
        $("a.project-add", this.el).click(this.onNewProjectClicked);
        scope = this;
        TeamsApiV2.project_list(TEAM_SLUG, null, this.onProjectListLoaded);
        this.projects = [];
        
    },
    addProject: function(pModel){
        var isNew = true;
        _.each(this.projects, function(m){
            if (pModel.pk == m.pk ){
                isNew = false;
            }
        });
        if (isNew){
            this.projects.push(pModel);
        }
    },
    renderProjectList: function(){
        var projectListing = $(".projects.listing", this.el);
        $("li", projectListing).remove();
        _.each(this.projects, function(x){
            var el = ich.projectListItem(x);
            projectListing.append(el);
        })
    },
    onProjectListLoaded: function(data){
        _.each(data, function(x){
            this.addProject(new ProjectModel(x))
        }, this);
        this.renderProjectList();
    },
    
    onNewProjectClicked : function(e){
        e.preventDefault();
        this.projectEditPanel  = new ProjectEditPanel(new ProjectModel({}));
        this.el.append(this.projectEditPanel.el);
        this.projectEditPanel.el.bind(ON_PROJECT_SAVED, this.onProjectSaved)
        return false;
    },
    onProjectSaved: function(e, p){
        this.projectEditPanel.el.unbind(ON_PROJECT_SAVED);
        this.projectEditPanel.el.remove();
        this.addProject(p);
        this.renderProjectList();
        
    }
});

var TabMenuItem = Class.$extend({
    __init__: function (data){
        this.el = ich.subMenuItem(data)[0];
        this.buttonEl = $("a", this.el)[0];
        this.klass = data.klass;
        this.panelEl = $(data.painelSelector);
    },
    markActive: function(isActive){
        if (isActive){
            $(this.el).addClass(ACTIVE_CLASS);
        }else{
            $(this.el).removeClass(ACTIVE_CLASS);
        }
    },
    showPanel: function(shows){
        if (shows){
            $(this.panelEl).show();
            if(this.klass){
                return  new this.klass();
            }
        }else{
            $(this.panelEl).hide();
        }
        return null;
    }
});

var TabViewer = Class.$extend({
    __init__: function(buttons, menuContainer, panelContainer){
        this.menuItems = _.map(buttons, function(x){
            var item = new TabMenuItem(x);
            $(menuContainer).append(item.el);
            return item;
        })
            
        $(menuContainer).click(_.bind(this.onClick, this));
        this.panelContainer = panelContainer;
    },
    openDefault: function(){
        $(this.menuItems[0].buttonEl).trigger("click");
    },
    onClick: function(e){
        e.preventDefault();
        var scope = this;
        if (this.currentItem){
            this.currentItem.showPanel(false);
            this.currentItem.markActive(false);
            if (this.currentKlass){
                this.currentKlass.hide();
            }
        }
        _.each(this.menuItems, function(x){
            if (x.buttonEl == e.target){
                x.markActive(true);
                this.currentKlass = x.showPanel(true);
                if (this.currentKlass){
                    this.panelContainer.append(this.currentKlass.el);
                }
                
                scope.currentItem = x;
            }

            return;
        }, this);
        
    }
});
    
function boostrapTabs(){
    var buttons = [
        {label:"Basic Settings", painelSelector:".painel-basic", klass:null},
        {label:"Guidelines and messages", painelSelector:".painel-guidelines", klass:null},
        {label:"Display Settings", painelSelector:".painel-display", klass:null},
        {label:"Projects", painelSelector:".painel-projects", klass:ProjectPainel}
        
    ]
    var viewer = new TabViewer(buttons, $(".sub-settings-panel"), $(CONTAINER_SELECTOR)) ;
    viewer.openDefault();
    
}

boostrapTabs();
