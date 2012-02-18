#! /bin/bash
:>rdi_target
for thing in 'vit' 'elem' 'macro'; do
	cat dri_table/rdi_target wikipedia/rdi_target >> rdi_target
done
