default: help

PATCH         = MiniMeBase.patch
CONTRACTS_DIR = ../contracts
MUNGED_DIR    = ./munged
MiniMeBase_origin = ../contracts/
MiniMeBase_munged = ./munged/
help:
	@echo "usage:"
	@echo "  make clean:  remove all generated files (those ignored by git)"
	@echo "  make $(MUNGED_DIR): create $(MUNGED_DIR) directory by applying the patch file to $(CONTRACTS_DIR)"
	@echo "  make record: record a new patch file capturing the differences between $(CONTRACTS_DIR) and $(MUNGED_DIR)"

munge:
	cp -R $(MiniMeBase_origin) $(MUNGED_DIR)
	patch -d $(MUNGED_DIR) < $(PATCH)

record:
	diff -burN $(MiniMeBase_origin) $(MiniMeBase_munged) | sed 's+\$(MiniMeBase_origin)/++g' | sed 's+$(MiniMeBase_munged)++g' > $(PATCH)
	
clean:
	git clean -fdX
	touch $(PATCH)