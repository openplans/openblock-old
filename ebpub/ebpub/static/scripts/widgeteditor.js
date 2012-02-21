var WidgetEditor = function(el, slug, rootURL) {
    this.el = el;
    this.slug = slug; 
    this.rootURL = rootURL;
    this.itemStart = 0;
    this.itemsToLoad = 25;
    this.maxPinnedItems = $(el).find('.current-items li').length;
    this.init();
};

WidgetEditor.prototype.init = function() {

    var thisWidget = this;

    $(this.el).find('.current-items').droppable({
        drop: function(event) {
            thisWidget.hookupCurrentItems();
        }
    }).sortable({
    	revert: 100,
        update: function(event) {
            thisWidget.fixLengthOfCurrentItems();
            thisWidget.savePins(true);
        }
    });

    $(this.el).find('.load-items').click(function() {
        thisWidget.loadMoreItems();
    });
    $(this.el).find('.save-button').live('click', function() {
        thisWidget.savePins(true);
    });
    this.loadMoreItems();
    this.loadStickyItems();
};

WidgetEditor.prototype.fixLengthOfCurrentItems = function() {
    while ($(this.el).find('.current-items li').length > this.maxPinnedItems) {
        $(this.el).find('.current-items li').last().remove();
    };
    while ($(this.el).find('.current-items li').length < this.maxPinnedItems) {
        $(this.el).find('.current-items li').last().append('<li class="empty-slot">Empty Slot</li>');
    };

};

WidgetEditor.prototype.hookupCurrentItems = function() {
    var thisWidget = this;
    $(this.el).find('.current-items .delete-button').click(function(evt) {
        evt.preventDefault();
        var theLi = $(evt.target).closest('li').remove();
        thisWidget.savePins(false);
        thisWidget.fixLengthOfCurrentItems();
        return false;
    });

    $(this.el).find('.current-items .expire-date').calendricalDate({usa: true});
    // Not using calendricalTime because it just interacts too poorly with
    // jqueryUI sorting and dropping, which is more important to us here.
    // Specifically, I haven't found a user-friendly way to switch between
    // dragging behavior and time-scrolling behavior.
    // So, let's just use a vanilla text widget.
    // $(this.el).find('.current-items .expire-time').calendricalTime(
    //     {usa: true, defaultTime: {hour: 12, minute: 0}});

};

WidgetEditor.prototype.savePins = function(do_reload) {
    var item_list = [];
    $(this.el).find('.current-items li').each(function(index, item) {
        if (!$(item).hasClass('empty-slot')) {
            var item_id = parseInt($(item).find('.item-id').text());
            var expiration_date = $(item).find('.expire-date').val();
            var expiration_time = $(item).find('.expire-time').val();
            item_list.push({
                id: item_id,
                index: index,
                expiration_date: expiration_date,
                expiration_time: expiration_time
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
            do_reload && document.location.reload();
        }
    });

};

WidgetEditor.prototype.htmlForItem = function(item) {
    var item_html = '<li class="pinnable-newsitem">';
    item_html += '<span class="item-id">' +  item.id +'</span>';
    item_html += ' <a target="_blank" href="/admin/db/newsitem/' + item.id + '">';
    item_html += item.title + '</a>';
    item_html += '<div class="expiration">Expiration Date:';
    item_html += '<input type="text" size="10" class="expire-date" ';
    if (item.expiration_date) {
        item_html += 'value="' + item.expiration_date + '"';
    }
    item_html += ' />';
    item_html += 'Time: <input type="text" class="expire-time" size="7" ';
    if (item.expiration_time) {
        item_html += ' value="' + item.expiration_time + '"';
    }
    item_html += ' />';
    item_html += '</div>';
    item_html += '<div class="buttons"><button class="save-button">Save</button>';
    item_html += '<button class="delete-button" alt="remove" title="remove">x</button>';
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
        // UNfortunately we can't just bind a handler that calls savePins()
        // on change, blur, etc. of the expiration inputs, because
        // Calendrical doesn't trigger any of those events.
	// Hopefully, saving on any button press will be enough.
        thisWidget.hookupCurrentItems();
        thisWidget.fixLengthOfCurrentItems();
    };

    $.ajax({
        url: pinsURL,
        type: "GET",
        dataType: "json",
        success: function(data) {
            handleItemsLoaded(data);
        }
    });

};

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
        // Text selection can interfere w/ dragging, but we need
        // it for our time input, so only apply this to the "available" column.
        $(thisWidget.el).find(".available-items li" ).disableSelection();

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
