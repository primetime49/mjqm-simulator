//
// Created by Marco Ciotola on 24/01/25.
//

#ifndef MJQM_SAMPLERS_PARETO_H
#define MJQM_SAMPLERS_PARETO_H

#include <cassert>
#include <memory>
#include <random>
#include "exponential.hpp"

class pareto : public exponential {
public:
    explicit pareto(std::shared_ptr<std::mt19937_64> generator, double alpha, double xm) :
        exponential(std::move(generator), 1 / alpha), alpha(alpha), xm(xm) {
        assert(alpha > 1); // otherwise the mean is infinite
    }

private:
    const double alpha;
    const double xm;
    const double mean = xm * alpha / (alpha - 1);
    const double variance = alpha > 2 ? std::pow(xm, 2) * alpha / (std::pow(alpha - 1, 2) * (alpha - 2))
                                      : std::numeric_limits<double>::infinity();

public:
    double d_mean() const override { return mean; }
    double d_variance() const override { return variance; }
    double sample() override { return xm * exp(exponential::sample()); }

    static std::shared_ptr<sampler> with_rate(std::shared_ptr<std::mt19937_64> generator, double rate, double alpha) {
        return std::make_shared<pareto>(std::move(generator), alpha, (alpha - 1) / alpha / rate);
    }
    static std::shared_ptr<sampler> with_mean(std::shared_ptr<std::mt19937_64> generator, double mean, double alpha) {
        return std::make_shared<pareto>(std::move(generator), alpha, (alpha - 1) / alpha * mean);
    }

    explicit operator std::string() const override {
        return "pareto (alpha=" + std::to_string(alpha) + " ; x_m=" + std::to_string(xm) +
            " => mean=" + std::to_string(mean) + " ; variance=" + std::to_string(variance) + ")";
    }
};

#endif // MJQM_SAMPLERS_PARETO_H
