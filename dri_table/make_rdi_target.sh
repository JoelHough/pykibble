#! /bin/bash
:>rdi_target
for thing in 'vit' 'elem' 'macro'; do
    paste -d "^" rda_${thing}_nuts rda_${thing}_vals rda_${thing}_weights | grep -v "^#" | sed -e "s/\(^.*\)\^\(.*\)\^\(.*$\)/~\1~\^~\2~\^~\3~/" >> rdi_target
done
