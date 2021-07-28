ifeq ($(RTE_SDK),)
	$(error "RTE_SDK not defined (might be that the environemnt variables were not set)")
endif

# Default target, can be overriden by command line or environment
RTE_TARGET ?= x86_64-native-linuxapp-gcc

include $(RTE_SDK)/mk/rte.vars.mk

# binary name
APP = median

# all source are stored in SRCS-y
SRCS-y := main.c median_hdr.c process_packet.c median.c median_errno.c

CFLAGS += -O3
CFLAGS += $(WERROR_FLAGS)

include $(RTE_SDK)/mk/rte.extapp.mk
