var WidgetEditor = function(el, slug, rootURL) {
    this.el = el;
    this.slug = slug; 
    this.rootURL = rootURL;
    this.itemStart = 0;
    this.itemsToLoad = 25;
    this.init();
};

WidgetEditor.prototype.SKELETON_HTML = '\
<div class="available-container">\
  <h2>Latest Items</h2>\
  <ul class="available-items"></ul>\
  <button class="load-items">Load More</button>\
</div>\
<div class="current-container">\
<h2>Pinned Items</h2>\
<ol class="current-items"></ol>\
<button class="save-button">Save</button>\
</div>';


WidgetEditor.prototype.init = function() {
    $(this.el).html(this.SKELETON_HTML);

    var thisWidget = this;
    $(this.el).find('.current-items').droppable({
        drop: function() {
            thisWidget.hookupCurrentItems();
        }
    }).sortable({
    	revert: true
    });


    for (var i = 0; i < this.itemsToLoad; i++) {
        $(this.el).find('.current-items').append('<li class="empty-slot">Empty Slot</li>');
    }

    var thisWidget = this;
    $(this.el).find('.load-items').click(function() {
        thisWidget.loadMoreItems();
    });
    $(this.el).find('.save-button').click(function() {
        thisWidget.savePins();
    });
    this.loadMoreItems();
    this.loadStickyItems(); 
};

WidgetEditor.prototype.hookupCurrentItems = function() {
    $(this.el).find('.current-items .delete-button').click(function(evt) {
        evt.preventDefault();
        var theLi = $(evt.target).closest('li').remove();
        return false;
    });
    
    $(this.el).find('.current-items .expire-date').calendricalDate({usa: true});
    $(this.el).find('.current-items .expire-time').calendricalTime({usa: true});
    
};

WidgetEditor.prototype.savePins = function() {
    var item_list = [];
    $(this.el).find('.current-items li').each(function(index, item) {
        if (!$(item).hasClass('empty-slot')) {
            var item_id = parseInt($(item).find('.item-id').text());
            var expire_date = $(item).find('.expire-date').val();
            var expire_time = $(item).find('.expire-time').val();
            item_list.push({
                id: item_id,
                index: index,
                expire_date: expire_date,
                expire_time: expire_time
            });
        }
    });
    var outPins = {items: item_list};
    
    var setPinsURL = this.rootURL + '/pins/' + this.slug;    
    $.ajax({
        url: setPinsURL,
        type: 'POST',
        data: JSON.stringify(outPins),
        dataType: 'json',
        success: function() {
            document.location.reload();
        }
    })
    
};


WidgetEditor.prototype.htmlForItem = function(item) {
    var item_html = '<li class="pinnable-newsitem">' + item.title;
    item_html += ' <a target="_blank" href="/admin/db/newsitem/' + item.id + '">view in admin</a>';
    item_html += '<span class="item-id">' +  item.id +'</span>';
    item_html += ' <a href="#" class="delete-button">Delete Pin</a>';
    item_html += '<div class="expiration">';
    item_html += '<h3>Expiration</h3>';
    item_html += '<input type="text" class="expire-date" '; 
    if (item.expiration_date) {
        item_html += 'value="' + item.expiration_date + '"';
    }
    item_html += ' />';
    item_html += '<input type="text" class="expire-time" '; 
    if (item.expiration_time) {
        item_html += 'value="' + item.expiration_time + '"';
    }
    item_html += ' />';
    item_html += '</div>';
    item_html += '</li>';
    return item_html;
};

WidgetEditor.prototype.loadStickyItems = function() {
    var pinsURL = this.rootURL + '/pins/' + this.slug;
    
    var thisWidget = this;
    var handleItemsLoaded = function(data) {
        for (var i =0; i < data.items.length; i++) {
            var item = data.items[i];
            var item_html = thisWidget.htmlForItem(item);
            $(item_html).insertBefore($(thisWidget.el).find('.current-items').children()[item.index]);
        }
        thisWidget.hookupCurrentItems();
    };
    
    $.ajax({
        url: pinsURL,
        type: "GET",
        dataType: "json",
        success: function(data) {
            handleItemsLoaded(data);
        }
    });
    
}

WidgetEditor.prototype.loadMoreItems = function() {
    var moreItemsURL = this.rootURL + '/raw_items/' + this.slug + '?start=' + this.itemStart + '&count=' + this.itemsToLoad;
    
    this.disableMoreButton();
    var thisWidget = this;
    var handleItemsLoaded = function(data) {
        for (var i =0; i < data.items.length; i++) {
            var item = data.items[i];
            var item_html = thisWidget.htmlForItem(item);
            $(thisWidget.el).find('.available-items').append(item_html);
            thisWidget.itemStart += 1;
        }
        
        $(thisWidget.el).find('.available-items li').draggable({
            connectToSortable: $(thisWidget.el).find(".current-items"),
    	    helper: "clone",
    	    revert: "invalid"
        });
        $(thisWidget.el).find("ul, ol, li" ).disableSelection();
    };
    
    $.ajax({
        url: moreItemsURL,
        type: "GET",
        dataType: "json",
        success: function(data) {
            handleItemsLoaded(data);
            thisWidget.enableMoreButton();
        }, 
        error: function() {
            thisWidget.enableMoreButton();
        }
    });
};


WidgetEditor.prototype.disableMoreButton = function() {
    $(this.el).find('.load-items').attr('disabled', 'disabled');
};

WidgetEditor.prototype.enableMoreButton = function() {
    $(this.el).find('.load-items').removeAttr('disabled');
};
