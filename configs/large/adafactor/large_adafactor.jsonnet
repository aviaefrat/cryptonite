local config = import "../large.jsonnet";

config {
    "trainer"+: {
        "optimizer": {
            "type": "adafactor",
            "lr": 0.001,               # From https://arxiv.org/pdf/1910.10683.pdf#page=9
            "scale_parameter": false,  #  "We use a constant learning rate of 0.001 when fine-tuning"
            "relative_step": false     #  also see https://github.com/pytorch/fairseq/blob/master/fairseq/optim/adafactor.py#L74
        }
    }
}
