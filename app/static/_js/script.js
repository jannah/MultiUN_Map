/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
//Fromhttp://stackoverflow.com/questions/2068272/getting-a-jquery-selector-for-an-element
jQuery.fn.getPath = function() {
    if (this.length != 1)
        throw 'Requires one element.';

    var path, node = this;
    while (node.length) {
        var realNode = node[0], name = realNode.localName;
        if (!name)
            break;
        name = name.toLowerCase();

        var parent = node.parent();

        var siblings = parent.children(name);
        if (siblings.length > 1) {
            name += ':eq(' + siblings.index(realNode) + ')';
        }

        path = name + (path ? '>' + path : '');
        node = parent;
    }

    return path;
};

$(document).on('ready', function() {
    init_mun();
})
function init_mun() {
    console.log('READY')
    console.log(doc)
    enableHighlight('.panel-body .value')
}
/*
 * inspired by 
 * http://stackoverflow.com/questions/8644428/how-to-highlight-text-using-javascript
 * @param {type} target
 * @returns {undefined}
 */
function enableHighlight(target)
{
//    var targets = $(target)
//    console.log(targets)
    $(target).on('click', function() {
        var self = $(this)
        var text = self.text();
        if (text.indexOf('<->') > -1)
        {

            var colloc = text.split(' <-> ');
            $('.highlight-key').removeClass('highlight-key');
//            self.addClass('highlight-key');
            for (var i = 0, j = colloc.length; i < j; i++)
            {
                console.log('tagging ' + colloc[i])

                $('.highlight-' + i).removeClass('highlight-' + i);

                console.log(self.getPath())
                highlight(colloc[i].trim(),
                        'highlight-' + i, [self.getPath(),
                            "#document-content"]);

            }
        }
        else {
            console.log(text)
            $('.highlight-key').removeClass('highlight-key');
            self.addClass('highlight-key');
            highlight(text, 'highlight', ["#document-content"]);
        }
//        console.log('clicking')

    })/*
     for(var i in targets)
     {
     var el = targets[i]
     $(el).on('click', function(){
     var text = $(this).text()
     console.log('highlighting '+text)
     $(this).addClass('highlight')
     })
     }*/
}
function highlight(text, hclass, targets)
{
    $('.' + hclass).removeClass(hclass)
    for (var t in targets)
    {
        var target = targets[t]
        hclass = hclass ? hclass : 'highlight';


//    inputText = document.getElementById(target)
//    inputText =$(target)
//    var innerHTML = inputText.innerHTML
        console.log(hclass)
        var innerHTML = $(target).html();
        var re = new RegExp(text, 'g');
        var html = "<span class='" + hclass + "'>" + text + "</span>";
//    inputText.innerHTML = innerHTML.replace(re, html);
        $(target).html(innerHTML.replace(re, html));
    }
    /*
     var index = innerHTML.indexOf(text);
     if ( index >= 0 )
     { 
     innerHTML = innerHTML.substring(0,index) + "<span class='highlight'>" + innerHTML.substring(index,index+text.length) + "</span>" + innerHTML.substring(index + text.length);
     inputText.innerHTML = innerHTML 
     }
     */
}
Histogram = function(target, data, width, height, title) {
    console.log(data);
//    console.log($(this).parent());

//    $(this).parent().append("TESTING")
    data.map(function(d, i, a) {
        a[i]['label'] = d.values + ' ' + d.key;
    });
    console.log(data);
    var w = width, titleH = 30, h = height - titleH;


    var max = d3.max(data, function(d)
    {
        //            console.log(d);
        return d.values;
    });
    var min = d3.min(data, function(d)
    {
        return d.values;
    });
    var yScale = d3.scale.ordinal().rangeBands([0, h], .1, 1)
            .domain(data.map(function(d)
            {
                return d.label;
            }));
//    var yLabels = data.map(function(d) {
////        console.log(d);
//        return d.values + ' ' + d.key;
//    })
//    console.log(yLabels)
    var xScale = d3.scale.linear().domain([0, max]).range([0, w]);
    var yAxis = d3.svg.axis().scale(yScale).orient('left')
//            .tickValues(yLabels);
    var svg = d3.select(target).append('svg')
            .attr({
                height: height, width: width, class: 'histogram'}
            );
    var title = svg.append('g').append('text')
            .attr({
                x: w / 2, y: titleH
            })
            .style({'text-anchor': 'middle'})
            .text(title);
    var bars = svg.append('g')
            .attr("transform", "translate(" + 0 + "," + titleH + ")")
            .selectAll('rect')
            .data(data).enter()
            .append('rect')
            .attr({
                x: 0,
                y: function(d) {
                    return yScale(d.label);
                },
                height: yScale.rangeBand(),
                width: function(d) {
                    return xScale(d.values);
                }
            })
            .on('click', function(d) {
                alert(d.label);
            })
    var yAxisGroup = svg.append('g').attr(
            {
                class: "y axis",
                width: w,
                height: h
            }).append("g")
            .attr("transform", "translate(" + 0 + "," + titleH + ")")
            .call(yAxis)
            .selectAll("text")
            .style("text-anchor", "start")
            .attr({"dx": "2em", "dy": ".2em", 'unselectable': 'on'})
            .classed('unselectable', true)
            .on('click', function(d) {
                alert(d);
            })
//            .attr("transform", function(d) {
//                return "rotate(45)";
//            });

}
